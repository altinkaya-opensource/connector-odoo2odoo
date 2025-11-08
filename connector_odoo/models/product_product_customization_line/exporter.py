# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductProductCustomizationLineExporter(Component):
    """Export product customization lines to external Odoo"""

    _name = "odoo.product.product.customization.line.exporter"
    _inherit = "odoo.exporter"
    _apply_on = "odoo.product.product.customization.line"

class ProductProductCustomizationLineExportMapper(Component):
    """Map customization line fields for export"""

    _name = "odoo.product.product.customization.line.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = "odoo.product.product.customization.line"

    direct = [
        ("x", "x"),
        ("y", "y"),
        ("quantity", "quantity"),
        ("total_price", "total_price"),
        ("active", "active"),
    ]

    @mapping
    def product_id(self, record):
        binder = self.binder_for("odoo.product.product")
        return {
            "product_id": binder.to_external(record.product_id, wrap=True),
        }

    @mapping
    def surface_id(self, record):
        binder = self.binder_for("odoo.product.surface")
        return {
            "surface_id": binder.to_external(record.surface_id, wrap=True),
        }

    @mapping
    def customization_process_id(self, record):
        binder = self.binder_for("odoo.customization.process")
        return {
            "customization_process_id": binder.to_external(record.customization_process_id, wrap=True),
        }
