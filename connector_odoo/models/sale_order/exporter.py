# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import only_create, mapping

_logger = logging.getLogger(__name__)


class OdooSaleOrderExporter(Component):
    _name = "odoo.sale.order.exporter"
    _inherit = "odoo.exporter"
    _apply_on = ["odoo.sale.order"]

    def _should_import(self):
        """Search for an existing reference on Odoo backend"""
        # This means that the exported sale order is deleted on Odoo backend.
        if self.binding.external_id and not bool(
            self.backend_adapter.search(
                model="sale.order", domain=[("id", "=", self.external_id)]
            )
        ):
            self.external_id = 0
            self.binding.write({"external_id": 0})

        # If it's exported but not binded, we should set external_id manually.
        if not self.binding.external_id:
            external_record = self.backend_adapter.search(
                model="sale.order",
                domain=[
                    ("name", "=", self.binding.name),
                ],
                limit=1,
            )
            if external_record:
                self.external_id = external_record[0]

        return super(OdooSaleOrderExporter, self)._should_import()

    def _export_dependencies(self):
        if not self.binding.partner_id:
            return

        partner_records = self.env["res.partner"]
        partner_fields = ["partner_id", "partner_invoice_id", "partner_shipping_id"]

        # try to collect all partners
        for field in partner_fields:
            partner_records |= self.binding[field]

        for record_partner in partner_records:
            self._export_dependency(record_partner, "odoo.res.partner")

    def _after_export(self):
        """Hook called after the export"""
        binding = self.binding
        if binding and binding.order_line:
            for line in binding.order_line:
                self._export_dependency(line, "odoo.sale.order.line")
        if binding and binding.transaction_ids:
            # Only export done Garanti transactions
            electronic_txs = binding.transaction_ids.filtered(
                lambda t: t.provider_id.code == "garanti" and t.state == "done"
            )
            credit_payment = binding.transaction_ids.filtered(
                lambda txn: txn.provider_id.id == 19
            )
            if electronic_txs:
                for tx in electronic_txs:
                    self._export_dependency(tx, "odoo.payment.transaction")

                # Bind payments with sale order
                exported_payments = electronic_txs.mapped(
                    "payment_id.bind_ids"
                ).filtered(lambda p: p.external_id)
                if exported_payments:
                    self.backend_adapter.write(
                        self.external_id,
                        {
                            "payment_ids": [
                                (6, 0, exported_payments.mapped("external_id"))
                            ],
                            "payment_term_id": 24,  # Kredi kartı ile tahsilat
                        },
                    )

            elif credit_payment:
                # Do nothing, keep mapped payment term
                pass

            else:
                self.backend_adapter.write(
                    self.external_id,
                    {
                        "payment_term_id": 23,  # Banka havalesi
                    },
                )

        execute_job = self.binding.odoo_id.active_job_ids.filtered(
            lambda j: "execute_method" in j.func_string
        )
        if execute_job:
            execute_job.run_next_job()


class SaleOrderExportMapper(Component):
    _name = "odoo.sale.order.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = ["odoo.sale.order"]

    direct = [
        ("name", "name"),
        ("sale_deci", "sale_deci"),
        ("sale_volume", "sale_volume"),
        ("sale_weight", "sale_weight"),
        ("delivery_rating_success", "delivery_rating_success"),
        ("access_token", "access_token"),
    ]

    # yigit: buraya artık gerek yok cunku sale.order.line'ı mapledik.
    # children = [("order_line", "order_line", "odoo.sale.order.line")]

    @only_create
    @mapping
    def state_create(self, record):
        """
        Durumu taslak olarak göndermeliyiz ki böylece action_confirm çağrıldığında
        durum düzgün bir şekilde güncellensin.
        """
        return {"state": "draft"}

    # We should NOT send the state field. It should be set to draft and then
    # action_%s should be called.
    # @mapping
    # def state(self, record):
    #     return {"state": record.state}

    @mapping
    def confirmation_date(self, record):
        vals = {}
        if record.confirmation_date:
            vals["confirmation_date"] = record.confirmation_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
        return vals

    @mapping
    def date_order(self, record):
        return {
            "date_order": record.date_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        }

    @mapping
    def pricelist_id(self, record):
        binder = self.binder_for("odoo.product.pricelist")
        pricelist_id = binder.to_external(record.pricelist_id, wrap=True)
        return {"pricelist_id": pricelist_id or 123}  # 123: Genel Fiyat Listesi

    @mapping
    def warehouse_id(self, record):
        vals = {"warehouse_id": 2}  # Sincan
        if record.carrier_id and "Merkez" in record.carrier_id.name:
            vals["warehouse_id"] = 1  # Merkez
        return vals

    @mapping
    def source_id(self, record):
        return {"source_id": 6}  # Online satış

    @mapping
    def partner_id(self, record):
        binder = self.binder_for("odoo.res.partner")

        return {
            "partner_id": binder.to_external(
                record.partner_id,
                wrap=True,
            ),
            "partner_invoice_id": binder.to_external(
                record.partner_invoice_id,
                wrap=True,
            ),
            "partner_shipping_id": binder.to_external(
                record.partner_shipping_id,
                wrap=True,
            ),
        }

    @mapping
    def carrier_id(self, record):
        if not record.carrier_id:
            return {"carrier_id": False}
        binder = self.binder_for("odoo.delivery.carrier")
        return {"carrier_id": binder.to_external(record.carrier_id, wrap=True)}

    @mapping
    def payment_term_id(self, record):
        if not record.payment_term_id:
            return {"payment_term_id": False}
        binder = self.binder_for("odoo.account.payment.term")
        return {
            "payment_term_id": binder.to_external(record.payment_term_id, wrap=True)
        }

    @mapping
    def client_order_ref(self, record):
        return {"client_order_ref": record.client_order_ref}

    @mapping
    def utm(self, record):
        vals = {
            "campaign_id": False,
            "medium_id": False,
            "source_id": False,
        }
        if record.campaign_id:
            binder = self.binder_for("odoo.utm.campaign")
            vals["campaign_id"] = binder.to_external(record.campaign_id, wrap=True)
        if record.medium_id:
            binder = self.binder_for("odoo.utm.medium")
            vals["medium_id"] = binder.to_external(record.medium_id, wrap=True)
        if record.source_id:
            binder = self.binder_for("odoo.utm.source")
            vals["source_id"] = binder.to_external(record.source_id, wrap=True)
        return vals

    @mapping
    def fiscal_position_id(self, record):
        vals = {"fiscal_position_id": False}
        binder = self.binder_for("odoo.account.fiscal.position")
        if record.fiscal_position_id:
            vals["fiscal_position_id"] = binder.to_external(
                record.fiscal_position_id, wrap=True
            )
        return vals
