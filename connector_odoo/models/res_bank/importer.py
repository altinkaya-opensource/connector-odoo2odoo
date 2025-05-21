# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ResBankBatchImporter(Component):
    _name = "odoo.res.bank.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.res.bank"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo banks %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class ResBankMapper(Component):
    _name = "odoo.res.bank.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.res.bank"

    direct = [
        ("fax", "fax"),
        ("name", "name"),
        ("street", "street"),
        ("street2", "street2"),
        ("zip", "zip"),
        ("city", "city"),
        ("email", "email"),
        ("phone", "phone"),
        ("active", "active"),
        ("bic", "bic"),
    ]

    @mapping
    def state(self, record):
        if not record.get("state"):
            return {"state": False}

        ctx = {"lang": self.backend_record.get_default_language_code()}
        remote_state = self.work.odoo_api.browse(
            model="res.country.state", res_id=record["state"][0]
        )
        state_record = (
            self.env["res.country.state"]
            .with_context(ctx)
            .search(
                [
                    "&",
                    ("name", "=", remote_state["name"]),
                    ("country_id", "=", self.env.ref("base.tr").id),
                ],
                limit=1,
            )
        )
        
        if not state_record:
            return {"state": False}

        return {"state": state_record.id}

    @mapping
    def country(self, record):
        if not record.get("country"):
            return {"country": False}

        return {"country": record["country"][0]}


class BankImporter(Component):
    """Import Odoo Bank"""

    _name = "odoo.res.bank.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.res.bank"

    def _import_dependencies(self, force=False):
        if state := self.odoo_record.get("state"):
            self._import_dependency(
                state[0],
                "odoo.res.country.state",
                force=force,
            )
        if country := self.odoo_record.get("country"):
            self._import_dependency(
                country[0],
                "odoo.res.country",
                force=force,
            )

        return super()._import_dependencies(force=force)
