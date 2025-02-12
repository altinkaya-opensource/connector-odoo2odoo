# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OdooProductAttributeGroup(models.Model):
    _queue_priority = 10
    _name = "odoo.product.attribute.group"
    _inherit = ["odoo.binding"]
    _inherits = {"product.attribute.group": "odoo_id"}
    _description = "Odoo Attribute Group"
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


class ProductAttributeGroup(models.Model):
    _inherit = "product.attribute.group"

    bind_ids = fields.One2many(
        comodel_name="odoo.product.attribute.group",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class ProductAttributeGroupAdapter(Component):
    _name = "odoo.product.attribute.group.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.product.attribute.group"

    _odoo_model = "product.attribute.group"

    # Set get_passive to True to get the passive records also.
    _get_passive = False
