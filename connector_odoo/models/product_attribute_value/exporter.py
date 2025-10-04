# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductAttributeValueExporter(Component):
    """Export product attribute values to external Odoo"""
    
    _name = "odoo.product.attribute.value.exporter"
    _inherit = "odoo.exporter"
    _apply_on = "odoo.product.attribute.value"



class ProductAttributeValueExportMapper(Component):
    """Map attribute value fields for export"""
    
    _name = "odoo.product.attribute.value.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = "odoo.product.attribute.value"

    direct = [
        ("name", "name"),
    ]

    @only_create
    @mapping
    def attribute_id(self, record):
        binder = self.binder_for("odoo.product.attribute")
        return {
            "attribute_id": binder.to_external(record.attribute_id, wrap=True),
        }


class OdooProductAttributeValueExporter(Component):
    _name = "odoo.product.attribute.value.exporter"
    _inherit = "odoo.exporter"
    _apply_on = ["odoo.product.attribute.value"]

    def _should_import(self):
        """Search for an existing reference on Odoo backend"""

        # This means that the exported attribute is deleted on Odoo backend.
        if self.binding.external_id and not bool(
            self.backend_adapter.search(
                model="product.attribute.value", domain=[("id", "=", self.external_id)]
            )
        ):
            self.external_id = None
            self.binding.write({"external_id": None})

        # If it's exported but not binded, we should set external_id manually.
        if not self.binding.external_id:
            external_record = self.backend_adapter.search(
                model="product.attribute.value",
                domain=[
                    ("name", "=", self.binding.name),
                    ("attribute_id", "=", self.binding.attribute_id.bind_ids.external_id),
                ],
                limit=1,
            )
            if external_record:
                self.external_id = external_record[0]

        return super()._should_import()
