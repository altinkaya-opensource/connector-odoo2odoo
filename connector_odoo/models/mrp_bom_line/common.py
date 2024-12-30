# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OdooMrpBomLine(models.Model):
    _queue_priority = 10
    _name = "odoo.mrp.bom.line"
    _inherit = "odoo.binding"
    _inherits = {"mrp.bom.line": "odoo_id"}
    _description = "External Odoo MRP BOM Line"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    def name_get(self):
        result = []
        for op in self:
            name = "{} (Backend: {})".format(
                op.odoo_id.display_name, op.backend_id.display_name
            )
            result.append((op.id, name))

        return result


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    bind_ids = fields.One2many(
        comodel_name="odoo.mrp.bom.line",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class MrpBomLineAdapter(Component):
    _name = "odoo.mrp.bom.line.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.mrp.bom.line"

    _odoo_model = "mrp.bom.line"

    # Set get_passive to True to get the passive records also.
    _get_passive = False

    # def search(self, domain=None, model=None, offset=0, limit=None, order=None):
    #     """Search records according to some criteria
    #     and returns a list of ids
    #
    #     :rtype: list
    #     """
    #     if domain is None:
    #         domain = []
    #     ext_filter = ast.literal_eval(
    #         str(self.backend_record.external_bom_line_domain_filter)
    #     )
    #     domain += ext_filter or []
    #     return super(MrpBomLineAdapter, self).search(
    #         domain=domain, model=model, offset=offset, limit=limit, order=order
    #     )


class MrpBomLineListener(Component):
    _name = "mrp.bom.line.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["mrp.bom.line"]
    _usage = "event.listener"