# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProductCategoryTableAttributeLinesBatchImporter(Component):
    _name = "odoo.product.category.table.attribute.lines.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.category.table.attribute.lines"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo catalog table attribute lines error %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class ProductCategoryTableAttributeLinesMapper(Component):
    _name = "odoo.product.category.table.attribute.lines.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.category.table.attribute.lines"

    direct = [
        ("sequence", "sequence"),
        ("hierarchy_level", "hierarchy_level"),
    ]

    @mapping
    def category_id(self, record):
        binder = self.binder_for("odoo.product.category")
        categ = binder.to_internal(record["category_id"][0], unwrap=True)
        return {"category_id": categ.id}

    @mapping
    def attribute_id(self, record):
        binder = self.binder_for("odoo.product.attribute")
        attr = binder.to_internal(record["attribute_id"][0], unwrap=True)
        return {"attribute_id": attr.id}


class ProductCategoryTableAttributeLinesImporter(Component):
    _name = "odoo.product.category.table.attribute.lines.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.category.table.attribute.lines"

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        self._import_dependency(
            self.odoo_record["category_id"][0],
            "odoo.product.category",
            force=force,
        )
        self._import_dependency(
            self.odoo_record["attribute_id"][0],
            "odoo.product.attribute",
            force=force,
        )
