import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class BaseMultiImageImageBatchImporter(Component):
    """Import the Odoo Base Multi Images.
    Import from a date
    """

    _name = "odoo.base_multi_image.image.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.base_multi_image.image"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        # We only want to import images that are related to products.
        domain += [
            [
                "owner_model",
                "in",
                ("product.template", "product.product", "product.category"),
            ]
        ]

        external_ids = self.backend_adapter.search(
            domain, model="base_multi_image.image"
        )
        _logger.info(
            "search for odoo base multi images %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            self._import_record(external_id, force=force)


class BaseMultiImageImageMapper(Component):
    _name = "odoo.base_multi_image.image.import.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = ["odoo.base_multi_image.image"]

    direct = [
        ("name", "name"),
        ("sequence", "sequence"),
        ("comments", "comments"),
        ("is_published", "is_published"),
        ("image_1920", "image_1920"),
    ]

    def _get_owner(self, record):
        binder = self.binder_for("odoo.%s" % record["owner_model"])
        owner = binder.to_internal(record["owner_id"])
        return owner

    # @mapping
    # def name(self, record):
    #     # Avoid duplicate names
    #     owner = self._get_owner(record)
    #     name = record.get("name", owner.name)
    #     if owner:
    #         exist_images = self.env["base_multi_image.image"].search(
    #             [
    #                 ("owner_model", "=", owner.odoo_id._name),
    #                 ("owner_id", "=", owner.odoo_id.id),
    #             ]
    #         )
    #         if name in exist_images.mapped("name"):
    #             name = "%s %s" % (name, record["id"])
    #     return {"name": name}

    @mapping
    def owner_ref_model(self, record):
        vals = {
            "owner_model": False,
            "owner_id": False,
        }
        owner = self._get_owner(record)
        if owner:
            vals["owner_model"] = record["owner_model"]
            vals["owner_id"] = owner.odoo_id.id
        return vals

    @mapping
    def product_variant_ids(self, record):
        vals = {}
        if variant_ids := record["product_variant_ids"]:
            binder = self.binder_for("odoo.product.product")
            variants = []
            for variant_id in variant_ids:
                variant = binder.to_internal(variant_id)
                if variant:
                    variants.append(variant.odoo_id.id)
            vals["product_variant_ids"] = [(6, 0, variants)]
        else:
            vals["product_variant_ids"] = False
        return vals

class BaseMultiImageImageImporter(Component):
    _name = "odoo.base_multi_image.image.importer"
    _inherit = "odoo.importer"
    _apply_on = ["odoo.base_multi_image.image"]

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        record = self.odoo_record
        if record["owner_model"] not in (
            "product.template",
            "product.product",
            "product.category",
        ):
            raise Exception(
                "The owner model of the image is not a product or a product template"
            )
        self._import_dependency(
            record["owner_id"], "odoo.%s" % record["owner_model"], force=force
        )
