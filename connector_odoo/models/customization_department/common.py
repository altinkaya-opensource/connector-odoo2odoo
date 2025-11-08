# Copyright 2025 Erol Develi (https://github.com/erlinberg)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooCustomizationDepartment(models.Model):
    _queue_priority = 7
    _name = "odoo.customization.department"
    _inherit = ["odoo.binding"]
    _inherits = {"customization.department": "odoo_id"}
    _description = "Odoo Customization Department"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    def resync(self):
        if self.backend_id.main_record == "odoo":
            return self.delayed_export_record(self.backend_id)
        else:
            return self.delayed_import_record(
                self.backend_id, self.external_id, force=True
            )


class CustomizationDepartment(models.Model):
    _inherit = "customization.department"

    bind_ids = fields.One2many(
        comodel_name="odoo.customization.department",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class OdooCustomizationDepartmentAdapter(Component):
    _name = "odoo.customization.department.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.customization.department"

    _odoo_model = "customization.department"

    # Set get_passive to True to get the passive records also.
    _get_passive = False
