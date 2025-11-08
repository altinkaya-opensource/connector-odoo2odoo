# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooProductSurface(models.Model):
    _queue_priority = 7
    _name = "odoo.product.surface"
    _inherit = ["odoo.binding"]
    _inherits = {"product.surface": "odoo_id"}
    _description = "Odoo Product Surface"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    bind_ids = fields.One2many(
        comodel_name="odoo.product.surface",
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


class ProductSurface(models.Model):
    _inherit = "product.surface"

    bind_ids = fields.One2many(
        comodel_name="odoo.product.surface",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class OdooProductSurfaceAdapter(Component):
    _name = "odoo.product.surface.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.product.surface"

    _odoo_model = "product.surface"

    # Set get_passive to True to get the passive records also.
    _get_passive = False

