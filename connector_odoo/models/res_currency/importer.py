# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ResCurrencyBatchImporter(Component):
    _name = "odoo.res.currency.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.res.currency"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo currencies %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class ResCurrencyMapper(Component):
    _name = "odoo.res.currency.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.res.currency"

    direct = [
        ("name", "name"),
        ("active", "active"),
        ("rounding", "rounding"),
        ("currency_unit_label", "currency_unit_label"),
        ("currency_subunit_label", "currency_subunit_label"),
        ("symbol", "symbol"),
        ("position", "position"),
        ("decimal_places", "decimal_places"),
    ]

    @only_create
    @mapping
    def check_res_currency_exists(self, record):
        res = {}
        currency_id = self.env["res.currency"].search(
            [
                ("name", "=", record["name"]),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
        )
        if len(currency_id) == 1:
            _logger.info(
                "Res currency found for %s : %s" % (record["name"], currency_id.name)
            )
            res.update({"odoo_id": currency_id.id})
        return res


class CurrencyImporter(Component):
    """Import Odoo Currency"""

    _name = "odoo.res.currency.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.res.currency"
