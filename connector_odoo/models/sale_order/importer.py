# Copyright 2013-2017 Camptocamp SA
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """Import the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    A priority is set on the jobs according to their level to rise the
    chance to have the top level pricelist imported first.
    """

    _name = "odoo.sale.order.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.sale.order"]
    _usage = "batch.importer"

    def run(self, domain=None, force=False):
        """Run the synchronization"""
        # exported_ids = self.model.search([("external_id", "!=", 0)]).mapped(
        #     "external_id"
        # )
        # domain += [("id", "in", exported_ids)]
        synced_partner_ext_ids = (
            self.env["odoo.res.partner"].search([]).mapped("external_id")
        )
        domain += [("partner_id", "in", synced_partner_ext_ids)]
        updated_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo sale orders %s returned %s items",
            domain,
            len(updated_ids),
        )
        for order_id in updated_ids:
            self._import_record(order_id, force=force)


class SaleOrderImportMapper(Component):
    _name = "odoo.sale.order.import.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.sale.order"

    direct = [
        ("date_order", "date_order"),
        ("confirmation_date", "confirmation_date"),
        ("name", "name"),
        ("state", "state"),
        ("order_state", "order_state"),
        ("sale_deci", "sale_deci"),
        ("sale_weight", "sale_weight"),
        ("sale_volume", "sale_volume"),
        ("client_order_ref", "client_order_ref"),
        ("access_token", "access_token"),
    ]

    @mapping
    def backend_fields(self, record):
        return {
            "backend_amount_total": record["amount_total"],
            "backend_amount_tax": record["amount_tax"],
            "backend_picking_count": len(record["picking_ids"]),
            "backend_date_order": record["date_order"],
            "backend_state": record["state"],
        }

    @only_create
    @mapping
    def odoo_id(self, record):
        order = self.env["sale.order"].search([("name", "=", record["name"])])
        _logger.info("found sale order %s for record %s" % (record["name"], record))
        if len(order) == 1:
            return {"odoo_id": order.id}

        return {}

    @mapping
    def pricelist_id(self, record):
        binder = self.binder_for("odoo.product.pricelist")
        pricelist_id = binder.to_internal(record["pricelist_id"][0], unwrap=True)
        return {"pricelist_id": pricelist_id.id}

    @mapping
    def payment_term_id(self, record):
        vals = {"payment_term_id": False}
        if record["payment_term_id"]:
            binder = self.binder_for("odoo.account.payment.term")
            payment_term_id = binder.to_internal(
                record["payment_term_id"][0], unwrap=True
            )
            vals["payment_term_id"] = payment_term_id.id
        return vals

    @mapping
    def partner_id(self, record):
        binder = self.binder_for("odoo.res.partner")
        return {
            "partner_id": binder.to_internal(
                record["partner_id"][0],
                unwrap=True,
            ).id,
            "partner_invoice_id": binder.to_internal(
                record["partner_invoice_id"][0],
                unwrap=True,
            ).id,
            "partner_shipping_id": binder.to_internal(
                record["partner_shipping_id"][0],
                unwrap=True,
            ).id,
        }

    @mapping
    def fiscal_position_id(self, record):
        vals = {"fiscal_position_id": False}
        if record["fiscal_position_id"]:
            binder = self.binder_for("odoo.account.fiscal.position")
            fiscal_position_id = binder.to_internal(
                record["fiscal_position_id"][0], unwrap=True
            )
            vals["fiscal_position_id"] = fiscal_position_id.id
        return vals

    @mapping
    def user_id(self, record):
        if not record["user_id"]:
            return {"user_id": False}
        binder = self.binder_for("odoo.res.users")
        return {"user_id": binder.to_internal(record["user_id"][0], unwrap=True).id}

    @mapping
    def utm(self, record):
        vals = {
            "campaign_id": False,
            "medium_id": False,
            "source_id": False,
        }
        if utm_campaign_id := record.get("campaign_id"):
            binder = self.binder_for("odoo.utm.campaign")
            local_campaign = binder.to_internal(utm_campaign_id[0], unwrap=True)
            if local_campaign:
                vals["campaign_id"] = local_campaign.id
        if utm_medium_id := record.get("medium_id"):
            binder = self.binder_for("odoo.utm.medium")
            local_medium = binder.to_internal(utm_medium_id[0], unwrap=True)
            if local_medium:
                vals["medium_id"] = local_medium.id
        if utm_source_id := record.get("source_id"):
            binder = self.binder_for("odoo.utm.source")
            local_source = binder.to_internal(utm_source_id[0], unwrap=True)
            if local_source:
                vals["source_id"] = local_source.id
        return vals


class SaleOrderImporter(Component):
    _name = "odoo.sale.order.importer"
    _inherit = "odoo.importer"
    _apply_on = ["odoo.sale.order"]

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        # pricelist
        self._import_dependency(
            self.odoo_record["pricelist_id"][0],
            "odoo.product.pricelist",
            force=force,
        )
        # partners
        partner_ids = list(
            {
                self.odoo_record["partner_id"][0],
                self.odoo_record["partner_shipping_id"][0],
                self.odoo_record["partner_invoice_id"][0],
            }
        )
        for partner_id in partner_ids:
            self._import_dependency(
                partner_id,
                "odoo.res.partner",
                force=force,
            )
        # payment term
        if self.odoo_record["payment_term_id"]:
            self._import_dependency(
                self.odoo_record["payment_term_id"][0],
                "odoo.account.payment.term",
                force=force,
            )
        # sale person
        if self.odoo_record["user_id"]:
            self._import_dependency(
                self.odoo_record["user_id"][0],
                "odoo.res.users",
                force=force,
            )

    def _after_import(self, binding, force=False):
        res = super()._after_import(binding, force)
        # Update the sale order lines
        if self.odoo_record["order_line"]:
            for line_id in self.odoo_record["order_line"]:
                self._import_dependency(
                    line_id,
                    "odoo.sale.order.line",
                    force=force,
                )
        # Compare state with backend_state
        binding._set_sale_state()
        return res
