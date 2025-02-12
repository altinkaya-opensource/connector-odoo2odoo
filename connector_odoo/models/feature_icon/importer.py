# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class FeatureIconBatchImporter(Component):
    _name = "odoo.feature.icon.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.feature.icon"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo feature icon error %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class FeatureIconMapper(Component):
    _name = "odoo.feature.icon.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.feature.icon"

    direct = [
        ("name", "name"),
        ("image", "image"),
    ]


class FeatureIconImporter(Component):
    _name = "odoo.feature.icon.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.feature.icon"
