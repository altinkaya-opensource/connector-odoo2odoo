# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooProductProductCustomizationLine(models.Model):
    _queue_priority = 7
    _name = "odoo.product.product.customization.line"
    _inherit = ["odoo.binding"]
    _inherits = {"product.product.customization.line": "odoo_id"}
    _description = "Odoo Product Product Customization Line"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    bind_ids = fields.One2many(
        comodel_name="odoo.product.product.customization.line",
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


class ProductProductCustomizationLine(models.Model):
    _inherit = "product.product.customization.line"

    bind_ids = fields.One2many(
        comodel_name="odoo.product.product.customization.line",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class OdooProductProductCustomizationLineAdapter(Component):
    _name = "odoo.product.product.customization.line.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.product.product.customization.line"

    _odoo_model = "product.product.customization.line"

    # Set get_passive to True to get the passive records also.
    _get_passive = True
