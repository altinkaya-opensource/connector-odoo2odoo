# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class BatchProductProductExporter(Component):
    _name = "odoo.product.product.batch.exporter"
    _inherit = "odoo.delayed.batch.exporter"
    _apply_on = ["odoo.product.product"]
    _usage = "batch.exporter"

    

class ProductProductExportMapper(Component):
    _name = "odoo.product.product.export.mapper"
    _inherit = "odoo.export.mapper"
    _apply_on = ["odoo.product.product"]

    direct = [
        # Required fields
        ("name", "name"),
        ("no_create_variants", "no_create_variants"),
        ("purchase_line_warn", "purchase_line_warn"),
        ("sale_line_warn", "sale_line_warn"),
        ("tracking", "tracking"),
        ("detailed_type", "detailed_type"),
        # Optional fields
        ("active", "active"),
        ("is_published", "is_published"),
        ("sale_ok", "sale_ok"),
        ("purchase_ok", "purchase_ok"),
    ]

    @only_create
    @mapping
    def product_details(self, record):
        return {
            "default_code": record.default_code or False,
            "image_1920": record.image_1920 or False,
            "state": record.state or False,
            "cnc_price": record.cnc_price or False,
            "print_price": record.print_price or False,
            "assembly_price": record.assembly_price or False,
            "paint_price": record.paint_price or False,
            "lasercut_price": record.lasercut_price or False,
            "laser_marking_price": record.laser_marking_price or False,
            "insert_installation_price": record.insert_installation_price or False,
            "total_customization_price": record.total_customization_price or False,
            "customization_prices_auto_update": record.customization_prices_auto_update
            or False,
        }

    # product.product.customization.line

    @mapping
    def product_template_attribute_value_ids(self, record):
        vals = {"product_template_attribute_value_ids": []}
        if record.product_template_attribute_value_ids:
            binder = self.binder_for("odoo.product.template.attribute.value")
            vals["product_template_attribute_value_ids"] = [
                binder.to_external(attr_val, wrap=True)
                for attr_val in record.product_template_attribute_value_ids
            ]
        return vals

    @mapping
    def product_tmpl_id(self, record):
        vals = {"product_tmpl_id": False}
        if record.product_tmpl_id:
            binder = self.binder_for("odoo.product.template")
            vals["product_tmpl_id"] = binder.to_external(
                record.product_tmpl_id, wrap=True
            )
        return vals

    @mapping
    def v_cari_urun(self, record):
        vals = {"v_cari_urun": False}
        if record.v_cari_urun:
            binder = self.binder_for("odoo.res.partner")
            vals["v_cari_urun"] = binder.to_external(record.v_cari_urun, wrap=True)
        return vals

    @mapping
    def categ_id(self, record):
        vals = {"categ_id": False}
        if record.categ_id:
            binder = self.binder_for("odoo.product.category")
            vals["categ_id"] = binder.to_external(record.categ_id, wrap=True)
        return vals

    @mapping
    def uom_id(self, record):
        vals = {"uom_id": False}
        if record.uom_id:
            binder = self.binder_for("odoo.uom.uom")
            vals["uom_id"] = binder.to_external(record.uom_id, wrap=True)
        return vals

    @mapping
    def uom_po_id(self, record):
        vals = {"uom_po_id": False}
        if record.uom_po_id:
            binder = self.binder_for("odoo.uom.uom")
            vals["uom_po_id"] = binder.to_external(record.uom_po_id, wrap=True)
        return vals


class OdooProductProductExporter(Component):
    _name = "odoo.product.product.exporter"
    _inherit = "odoo.exporter"
    _apply_on = ["odoo.product.product"]

    def _must_skip(self):
        if self.binding and not self.binding.v_cari_urun:
            return True

        return super()._must_skip()

    def _export_dependencies(self):
        if self.binding.v_cari_urun:
            self._export_dependency(self.binding.v_cari_urun, "odoo.res.partner")

        for line in self.binding.product_tmpl_id.attribute_line_ids.filtered(
            lambda al: al.attribute_id.custom_production
        ):
            for attr_val in line.value_ids:
                self._export_dependency(attr_val, "odoo.product.attribute.value")
            self._export_dependency(line, "odoo.product.template.attribute.line")

    def _after_export(self, binding, force):
        if binding and binding.customization_line_ids:
            for line in binding.customization_line_ids:
                self.delayed_export_record(
                    self.backend_record,
                    line,
                    force=force,
                )

    def _create_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_create`"""
        datas = map_record.values(for_create=True, fields=fields, **kwargs)
        return datas
