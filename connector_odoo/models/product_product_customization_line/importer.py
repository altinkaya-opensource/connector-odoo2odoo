import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from lxml.html.clean import Cleaner

_logger = logging.getLogger(__name__)


class ProductProductCustomizationLineBatchImporter(Component):
    _name = "odoo.product.product.customization.line.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.product.customization.line"]


class ProductProductCustomizationLineImporter(Component):
    """Import Odoo Product Customization Line"""

    _name = "odoo.product.product.customization.line.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.product.customization.line"

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        record = self.odoo_record
        if product_id := record.get("product_id"):
            self._import_dependency(
                product_id[0], "odoo.product.product", force=force
            )

        if customization_id := record.get("customization_id"):
            self._import_dependency(
                customization_id[0], "odoo.customization.process", force=force
            )

        if surface_id := record.get("surface_id"):
            self._import_dependency(
                surface_id[0], "odoo.product.surface", force=force
            )


class ProductProductCustomizationLineMapper(Component):
    _name = "odoo.product.product.customization.line.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.product.customization.line"

    direct = [
        ("x", "x"),
        ("y", "y"),
        ("quantity", "quantity"),
        ("total_price", "total_price")
    ]

    @mapping
    def product_id(self, record):
        binder = self.binder_for("odoo.product.product")
        product = binder.to_internal(record.get("product_id")[0], unwrap=True)
        return {"product_id": product.id}

    @mapping
    def customization_process_id(self, record):
        binder = self.binder_for("odoo.customization.process")
        customization = binder.to_internal(record.get("customization_process_id")[0], unwrap=True)
        return {"customization_process_id": customization.id}

    @mapping
    def surface_id(self, record):
        binder = self.binder_for("odoo.product.surface")
        surface = binder.to_internal(record.get("surface_id")[0], unwrap=True)
        return {"surface_id": surface.id}
