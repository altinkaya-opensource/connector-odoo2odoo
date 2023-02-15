# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ResCurrencyRateBatchImporter(Component):
    _name = "odoo.res.currency.rate.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.res.currency.rate"]


class ResCurrencyRateMapper(Component):
    _name = "odoo.res.currency.rate.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.res.currency.rate"

    direct = [
        ("name", "name"),
        ("rate", "rate"),
    ]

    @only_create
    @mapping
    def check_currency_rate_exists(self, record):
        res = {}

        rate_id = self.env["res.currency.rate"].search([("name", "=", record.name)])
        _logger.info("Res currency rate found for %s : %s" % (record, rate_id))
        if len(rate_id) == 1:
            res.update({"odoo_id": rate_id.id})
        return res

    @only_create
    @mapping
    def currency_id(self, record):
        return {"currency_id": record.currency_id.id}


class CurrencyRateImporter(Component):
    """Import Odoo Currency"""

    _name = "odoo.res.currency.rate.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.res.currency.rate"

    def _init_import(self, binding, external_id):
        currency_rate = self.work.odoo_api.api.env["res.currency.rate"]
        rate_ids = currency_rate.search(
            [("currency_id", "=", external_id)], order="id desc"
        )
        total = len(rate_ids)
        _logger.info(
            "{} Currency rates found for external currency {}".format(
                total, external_id
            )
        )
        if rate_ids:
            i = 0
            for rate_id in rate_ids:
                i += 1
                _logger.info(
                    "Sending currency rate {} of {} to be processed as a new job".format(
                        i, total
                    )
                )
                self.env["odoo.res.currency.rate"].with_delay().import_rate(
                    currency_rate,
                    self.backend_record,
                    rate_id,
                    external_id
                )
        super()._init_import(binding, external_id)
        return False