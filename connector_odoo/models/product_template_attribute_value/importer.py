# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class ProductTemplateAttributeValueBatchImporter(Component):
    _name = "odoo.product.template.attribute.value.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = "odoo.product.template.attribute.value"


class ProductTemplateAttributeValueImporter(Component):
    _name = "odoo.product.template.attribute.value.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.template.attribute.value"

    def _import_dependencies(self):
        """Import dependencies first"""
        if self.odoo_record.get("product_attribute_value_id"):
            self._import_dependency(
                self.odoo_record["product_attribute_value_id"][0],
                "odoo.product.attribute.value"
            )
        
        if self.odoo_record.get("attribute_line_id"):
            self._import_dependency(
                self.odoo_record["attribute_line_id"][0],
                "odoo.product.template.attribute.line"
            )


class ProductTemplateAttributeValueImportMapper(Component):
    _name = "odoo.product.template.attribute.value.import.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.template.attribute.value"

    direct = []

    @mapping
    def product_attribute_value_id(self, record):
        binder = self.binder_for("odoo.product.attribute.value")
        return {
            "product_attribute_value_id": binder.to_internal(
                record["product_attribute_value_id"][0], unwrap=True
            ),
        }

    @mapping
    def attribute_line_id(self, record):
        binder = self.binder_for("odoo.product.template.attribute.line")
        return {
            "attribute_line_id": binder.to_internal(
                record["attribute_line_id"][0], unwrap=True
            ),
        }