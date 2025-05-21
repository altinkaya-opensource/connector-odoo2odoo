# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooResCountry(models.Model):
    _queue_priority = 10
    _name = "odoo.res.country"
    _inherit = ["odoo.binding"]
    _inherits = {"res.country": "odoo_id"}
    _description = "Odoo Country"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    def resync(self):
        if self.backend_id.main_record == "odoo":
            raise NotImplementedError
        else:
            return self.delayed_import_record(
                self.backend_id, self.external_id, force=True
            )


class ResCountry(models.Model):
    _inherit = "res.country"

    bind_ids = fields.One2many(
        comodel_name="odoo.res.country",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class ResCountryAdapter(Component):
    _name = "odoo.res.country.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.res.country"

    _odoo_model = "res.country"

    _get_passive = False
