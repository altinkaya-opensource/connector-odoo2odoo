# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductTemplateAttributeLineExporter(Component):
    _name = "odoo.product.template.attribute.line.exporter"
    _inherit = "odoo.exporter"
    _apply_on = "odoo.product.template.attribute.line"

    def _export_dependencies(self):
        for value in self.binding.value_ids:
            self._export_dependency(
                value,
                "odoo.product.attribute.value"
            )


class ProductTemplateAttributeLineExportMapper(Component):
    _name = "odoo.product.template.attribute.line.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = "odoo.product.template.attribute.line"

    direct = []

    @only_create
    @mapping
    def product_tmpl_id(self, record):
        binder = self.binder_for("odoo.product.template")
        return {
            "product_tmpl_id": binder.to_external(record.product_tmpl_id, wrap=True),
        }

    @only_create
    @mapping
    def attribute_id(self, record):
        binder = self.binder_for("odoo.product.attribute")
        return {
            "attribute_id": binder.to_external(record.attribute_id, wrap=True),
        }

    @mapping
    def value_ids(self, record):
        if not record.value_ids:
            return {"value_ids": []}
            
        binder = self.binder_for("odoo.product.attribute.value")
        external_ids = []
        
        for value in record.value_ids:
            external_id = binder.to_external(value, wrap=True)
            if external_id:
                external_ids.append(external_id)
        
        return {"value_ids": [(6, 0, external_ids)]}