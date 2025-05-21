# Copyright 2022 Greenice, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models

from odoo.addons.component.core import Component


class OdooResPartnerBank(models.Model):
    _queue_priority = 10
    _name = "odoo.res.partner.bank"
    _inherit = ["odoo.binding"]
    _inherits = {"res.partner.bank": "odoo_id"}
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


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bind_ids = fields.One2many(
        comodel_name="odoo.res.partner.bank",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class ResPartnerBankAdapter(Component):
    _name = "odoo.res.partner.bank.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.res.partner.bank"

    _odoo_model = "res.partner.bank"

    _get_passive = True
