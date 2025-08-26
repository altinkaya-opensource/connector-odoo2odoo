from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError


class ProductSurfaceBatchImporter(Component):
    _name = "odoo.product.surface.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.surface"]


class ProductSurfaceImporter(Component):
    _name = "odoo.product.surface.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.surface"

    def _import_dependencies(self, force=False):
        record = self.odoo_record

        if record.get("process_ids"):
            for process_id in record["process_ids"]:
                self._import_dependency(
                    process_id, "odoo.customization.process", force=force
                )


class ProductSurfaceMapper(Component):
    _name = "odoo.product.surface.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.surface"

    direct = [
        ("name", "name"),
        ("sequence", "sequence"),
        ("surface_material_type", "surface_material_type"),
        ("x", "x"),
        ("y", "y"),
        ("technical_drawing", "technical_drawing"),
    ]

    @mapping
    def product_tmpl_id(self, record):
        binder = self.binder_for("odoo.product.template")
        product_tmpl = binder.to_internal(record["product_tmpl_id"][0], unwrap=True)
        return {"product_tmpl_id": product_tmpl.id}

    @mapping
    def bom_component_product_id(self, record):
        vals = {"bom_component_product_id": False}
        if bom_component_product := record.get("bom_component_product_id"):
            binder = self.binder_for("odoo.product.product")
            vals["bom_component_product_id"] = binder.to_internal(
                bom_component_product[0], unwrap=True
            ).id
        return vals

    @mapping
    def process_ids(self, record):
        vals = {"process_ids": False}
        binder = self.binder_for("odoo.customization.process")
        if record.get("process_ids"):
            process_ids = []
            binder = self.binder_for("odoo.customization.process")
            for process in record["process_ids"]:
                local_process_id = binder.to_internal(process, unwrap=True)
                if not local_process_id:
                    raise MappingError(
                        f"The process with Odoo id {process.id} is not imported."
                    )
                process_ids.append(local_process_id.id)

            vals["process_ids"] = [(6, 0, process_ids)]
        return vals
