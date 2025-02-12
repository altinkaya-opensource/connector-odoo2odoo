# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProductAttributeGroupBatchImporter(Component):
    _name = "odoo.product.attribute.group.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.attribute.group"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo attribute group error %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class ProductAttributeGroupMapper(Component):
    _name = "odoo.product.attribute.group.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.attribute.group"

    direct = [
        ("name", "name"),
        ("sequence", "sequence"),
    ]


class ProductAttributeGroupImporter(Component):
    _name = "odoo.product.attribute.group.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.attribute.group"
