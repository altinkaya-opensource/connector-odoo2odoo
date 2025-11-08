# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class BatchProductTemplateAttributeValueExporter(Component):
    _name = "odoo.product.template.attribute.value.batch.exporter"
    _inherit = "odoo.delayed.batch.exporter"
    _apply_on = ["odoo.product.template.attribute.value"]
    _usage = "batch.exporter"


class ProductTemplateAttributeValueExportMapper(Component):
    _name = "odoo.product.template.attribute.value.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = ["odoo.product.template.attribute.value"]

    @only_create
    @mapping
    def product_attribute_value_id(self, record):
        binder = self.binder_for("odoo.product.attribute.value")
        return {
            "product_attribute_value_id": binder.to_external(
                record.product_attribute_value_id, wrap=True
            ),
        }

    @only_create
    @mapping
    def attribute_line_id(self, record):
        binder = self.binder_for("odoo.product.template.attribute.line")
        return {
            "attribute_line_id": binder.to_external(
                record.attribute_line_id, wrap=True
            ),
        }


class OdooProductTemplateAttributeValueExporter(Component):
    _name = "odoo.product.template.attribute.value.exporter"
    _inherit = "odoo.exporter"
    _apply_on = ["odoo.product.template.attribute.value"]

    def _export_dependencies(self):
        if self.binding.product_attribute_value_id:
            self._export_dependency(
                self.binding.product_attribute_value_id,
                "odoo.product.attribute.value"
            )
        
        if self.binding.attribute_line_id:
            self._export_dependency(
                self.binding.attribute_line_id,
                "odoo.product.template.attribute.line"
            )

    def _should_import(self):
        """Search for an existing reference on Odoo backend"""

        # If it's exported but not binded, we should set external_id manually.
        
        if not self.binding.external_id:
            external_record = self.backend_adapter.search(
                model="product.template.attribute.value",
                domain=[
                    ("attribute_line_id", "=",
                     self.binding.attribute_line_id.bind_ids.external_id),
                    ("product_attribute_value_id", "=",
                     self.binding.product_attribute_value_id.bind_ids.external_id),
                ],
                limit=1,
            )
            if external_record:
                self.external_id = external_record[0]

        return super()._should_import()
