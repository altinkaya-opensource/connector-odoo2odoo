# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ResCountryBatchImporter(Component):
    _name = "odoo.res.country.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.res.country"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo countries %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class ResCountryMapper(Component):
    _name = "odoo.res.country.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.res.country"

    direct = [
        ("name", "name"),
        ("code", "code"),
        ("phone_code", "phone_code"),
        ("vat_label", "vat_label"),
        ("zip_required", "zip_required"),
        ("state_required", "state_required"),
        ("address_format", "address_format"),
        ("name_position", "name_position"),
    ]

    @only_create
    @mapping
    def check_res_country_exists(self, record):
        res = {}
        country_id = self.env["res.country"].search(
            [
                ("code", "=", record["code"]),
            ]
        )
        if len(country_id) == 1:
            _logger.info(
                "Res country found for %s : %s" % (record["code"], country_id.code)
            )
            res.update({"odoo_id": country_id.id})
        return res

    @mapping
    def currency_id(self, record):
        vals = {"currency_id": False}
        if record.get("currency_id"):
            binder = self.binder_for("odoo.res.currency")
            currency_id = binder.to_internal(record["currency_id"][0], unwrap=True)
            vals.update({"currency_id": currency_id.id})
        return vals

    @mapping
    def default_eur_bank_account_id(self, record):
        vals = {"default_eur_bank_account_id": False}
        if record.get("default_eur_bank_account_id"):
            binder = self.binder_for("odoo.res.partner.bank")
            default_eur_bank_account_id = binder.to_internal(
                record["default_eur_bank_account_id"][0], unwrap=True)
            vals.update({"default_eur_bank_account_id": default_eur_bank_account_id.id})
        return vals

    @mapping
    def default_usd_bank_account_id(self, record):
        vals = {"default_usd_bank_account_id": False}
        if record.get("default_usd_bank_account_id"):
            binder = self.binder_for("odoo.res.partner.bank")
            default_usd_bank_account_id = binder.to_internal(
                record["default_usd_bank_account_id"][0], unwrap=True)
            vals.update({"default_usd_bank_account_id": default_usd_bank_account_id.id})
        return vals

    @mapping
    def default_try_bank_account_id(self, record):
        vals = {"default_try_bank_account_id": False}
        if record.get("default_try_bank_account_id"):
            binder = self.binder_for("odoo.res.partner.bank")
            default_try_bank_account_id = binder.to_internal(
                record["default_try_bank_account_id"][0], unwrap=True)
            vals.update({"default_try_bank_account_id": default_try_bank_account_id.id})
        return vals


class CountryImporter(Component):
    """Import Odoo Country"""

    _name = "odoo.res.country.importer"
    _inherit = "odoo.importer"
    _apply_on = ["odoo.res.country"]

    def _import_dependencies(self, force=False):
        if currency_id := self.odoo_record.get("currency_id"):
            self._import_dependency(
                currency_id[0],
                "odoo.res.currency",
                force=force,
            )

        if default_eur_bank_account_id := self.odoo_record.get("default_eur_bank_account_id"):
            self._import_dependency(
                default_eur_bank_account_id[0],
                "odoo.res.partner.bank",
                force=force,
            )

        if default_usd_bank_account_id := self.odoo_record.get("default_usd_bank_account_id"):
            self._import_dependency(
                default_usd_bank_account_id[0],
                "odoo.res.partner.bank",
                force=force,
            )
            
        if default_try_bank_account_id := self.odoo_record.get("default_try_bank_account_id"):
            self._import_dependency(
                default_try_bank_account_id[0],
                "odoo.res.partner.bank",
                force=force,
            )

        return super()._import_dependencies(force=force)
