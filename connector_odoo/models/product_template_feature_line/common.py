from odoo import fields, models

from odoo.addons.component.core import Component


class OdooProductTemplateFeatureLine(models.Model):
    _queue_priority = 5
    _name = "odoo.product.template.feature.line"
    _inherit = ["odoo.binding"]
    _inherits = {"product.template.feature.line": "odoo_id"}
    _description = "Odoo Product Template Feature Line"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    bind_ids = fields.One2many(
        comodel_name="odoo.product.template.feature.line",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )

    def resync(self):
        if self.backend_id.main_record == "odoo":
            return self.delayed_export_record(self.backend_id)
        else:
            return self.delayed_import_record(
                self.backend_id, self.external_id, force=True
            )


class ProductFeatureLine(models.Model):
    _inherit = "product.template.feature.line"

    bind_ids = fields.One2many(
        comodel_name="odoo.product.template.feature.line",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class OdooProductFeatureAdapter(Component):
    _name = "odoo.product.template.feature.line.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.product.template.feature.line"

    _odoo_model = "product.template.feature.line"

    # Set get_passive to True to get the passive records also.
    _get_passive = False
