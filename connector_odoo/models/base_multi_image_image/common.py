import logging
from odoo import fields, models
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OdooBaseMultiImageImage(models.Model):
    """
    This is the real mapping model for product images on version 16.0
    You can avoid product.image model and use this model instead.
    """

    _name = "odoo.base_multi_image.image"
    _inherit = "odoo.binding"
    _inherits = {"base_multi_image.image": "odoo_id"}
    _description = "External Odoo Base Multi Images"
    _sql_constraints = [
        (
            "external_id",
            "UNIQUE(external_id)",
            "External ID (external_id) must be unique!",
        ),
    ]

    def resync(self):
        if self.backend_id.main_record == "odoo":
            return self.with_delay().export_record(self.backend_id)
        else:
            return self.with_delay().import_record(
                self.backend_id, self.external_id, force=True
            )

    def create(self, vals):
        return super().create(vals)


class BaseMultiImageImage(models.Model):
    _inherit = "base_multi_image.image"

    bind_ids = fields.One2many(
        comodel_name="odoo.base_multi_image.image",
        inverse_name="odoo_id",
        string="Odoo Bindings",
    )


class BaseMultiImageImageAdapter(Component):
    _name = "odoo.base_multi_image.image.adapter"
    _inherit = "odoo.adapter"
    _apply_on = "odoo.base_multi_image.image"

    _odoo_model = "base_multi_image.image"


class ProductImageListener(Component):
    _name = "base_multi_image.image.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["base_multi_image.image"]
    _usage = "event.listener"