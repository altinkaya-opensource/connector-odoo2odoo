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

    def run(self, filters=None, force=False):
        """Run the synchronization"""

        # We only want to import images that are related to products.
        filters += [["owner_model", "in", ("product.template", "product.product")]]

        external_ids = self.backend_adapter.search(
            filters, model="base_multi_image.image"
        )
        _logger.info(
            "search for odoo base multi images %s returned %s items",
            filters,
            len(external_ids),
        )
        for external_id in external_ids:
            job_options = {"priority": 15}
            self._import_record(external_id, job_options=job_options, force=force)


class BaseMultiImageImageMapper(Component):
    _name = "odoo.base_multi_image.image.import.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = ["odoo.base_multi_image.image"]

    direct = [
        ("sequence", "sequence"),
        ("storage", "storage"),
        ("extension", "extension"),
        ("comments", "comments"),
    ]

    @mapping
    def name(self, record):
        if record.name:
            return {"name": record.name}
        else:
            return {"name": record.owner_ref_id.name}

    @mapping
    def owner_ref_model(self, record):
        vals = {}
        binder = self.binder_for("odoo.%s" % record.owner_model)
        owner = binder.to_internal(record.owner_id)
        if owner:
            vals["owner_model"] = record.owner_model
            vals["owner_id"] = owner.odoo_id.id
        return vals

    @mapping
    def attachment_id(self, record):
        vals = {}
        if record.attachment_id:
            binder = self.binder_for("odoo.ir.attachment")
            attachment = binder.to_internal(record.attachment_id.id)
            if not attachment:
                attachment = self.env["odoo.ir.attachment"].search(
                    [("store_fname", "=", record.attachment_id.store_fname)],
                    limit=1
                )
            vals["attachment_id"] = attachment.odoo_id.id
        return vals

    @mapping
    def file_db_store(self, record):
        vals = {}
        if record.storage == "db" and record.file_db_store:
            vals["file_db_store"] = record.file_db_store
        return vals

    @mapping
    def product_variant_ids(self, record):
        vals = {}
        if record.product_variant_ids:
            binder = self.binder_for("odoo.product.product")
            variants = []
            for variant in record.product_variant_ids:
                variant = binder.to_internal(variant.id)
                if variant:
                    variants.append(variant.odoo_id.id)
            vals["product_variant_ids"] = [(6, 0, variants)]
        return vals


class BaseMultiImageImageImporter(Component):
    _name = "odoo.base_multi_image.image.importer"
    _inherit = "odoo.importer"
    _apply_on = ["odoo.base_multi_image.image"]

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        record = self.odoo_record
        if record.owner_model not in ("product.template", "product.product"):
            raise Exception(
                "The owner model of the image is" " not a product or a product template"
            )
        self._import_dependency(
            record.owner_id, "odoo.%s" % record.owner_model, force=force
        )
        # We need to import the attachment as well.
        if record.attachment_id:
            self._import_dependency(
                record.attachment_id.id, "odoo.ir.attachment", force=force
            )

        if record.product_variant_ids:
            for variant in record.product_variant_ids:
                self._import_dependency(variant.id, "odoo.product.product", force=force)