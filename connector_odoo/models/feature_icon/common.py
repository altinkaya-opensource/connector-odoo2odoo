# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OdooFeatureIcon(models.Model):
    _queue_priority = 10
    _name = "odoo.feature.icon"
    _inherit = ["odoo.binding"]
    _inherits = {"feature.icon": "odoo_id"}
    _description = "Odoo Feature Icon"
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


class FeatureIcon(models.Model):
    _inherit = "feature.icon"

    bind_ids = fields.One2many(
        comodel_name="odoo.feature.icon",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class FeatureIconAdapter(Component):
    _name = "odoo.feature.icon.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.feature.icon"

    _odoo_model = "feature.icon"

    # Set get_passive to True to get the passive records also.
    _get_passive = False
