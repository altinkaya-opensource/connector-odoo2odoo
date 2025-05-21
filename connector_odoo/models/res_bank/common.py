# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooResBank(models.Model):
    _queue_priority = 10
    _name = "odoo.res.bank"
    _inherit = ["odoo.binding"]
    _inherits = {"res.bank": "odoo_id"}
    _description = "Odoo Bank"
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


class ResBank(models.Model):
    _inherit = "res.bank"

    bind_ids = fields.One2many(
        comodel_name="odoo.res.bank",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class ResBankAdapter(Component):
    _name = "odoo.res.bank.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.res.bank"

    _odoo_model = "res.bank"

    _get_passive = False
