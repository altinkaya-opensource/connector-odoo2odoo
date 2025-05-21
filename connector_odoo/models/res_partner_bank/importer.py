# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ResPartnerBankBatchImporter(Component):
    _name = "odoo.res.partner.bank.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.res.partner.bank"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo partner banks %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)

class ResPartnerBankMapper(Component):
    _name = "odoo.res.partner.bank.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.res.partner.bank"

    direct = [
        ("acc_number", "acc_number"),
        ("acc_holder_name", "acc_holder_name"),
        ("allow_out_payment", "allow_out_payment"),
    ]

    @mapping
    def bank_id(self, record):
        vals = {"bank_id": False}
        binder = self.binder_for("odoo.res.bank")
        if bank := record["bank_id"]:
            bank_id = binder.to_internal(bank[0], unwrap=True)
            vals["bank_id"] = bank_id.id

        return vals

    @mapping
    def partner_id(self, record):
        vals = {"partner_id": False}
        binder = self.binder_for("odoo.res.partner")
        if partner := record["partner_id"]:
            partner_id = binder.to_internal(partner[0], unwrap=True)
            vals["partner_id"] = partner_id.id

        return vals

    @mapping
    def currency_id(self, record):
        vals = {"currency_id": False}
        if record.get("currency_id"):
            binder = self.binder_for("odoo.res.currency")
            currency_id = binder.to_internal(record["currency_id"][0], unwrap=True)
            vals.update({"currency_id": currency_id.id})
        return vals


class BankImporter(Component):
    """Import Odoo Bank"""

    _name = "odoo.res.partner.bank.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.res.partner.bank"

    def _import_dependencies(self, force=False):
        self._import_dependency(
            self.odoo_record["partner_id"][0],
            "odoo.res.partner",
            force=force,
        )
        if bank_id := self.odoo_record.get("bank_id"):
            self._import_dependency(
                bank_id[0],
                "odoo.res.bank",
                force=force,
            )
        if currency_id := self.odoo_record.get("currency_id"):
            self._import_dependency(
                currency_id[0],
                "odoo.res.currency",
                force=force,
            )
        return super()._import_dependencies(force=force)
