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
