# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from lxml.html.clean import Cleaner

_logger = logging.getLogger(__name__)


class ProductAttributeValueBatchImporter(Component):
    _name = "odoo.product.attribute.value.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.attribute.value"]

    def run(self, domain=None, force=False):    
        """Run the synchronization"""
        external_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo products attribute values %s returned %s items",
            domain,
            len(external_ids),
        )
        for external_id in external_ids:
            job_options = {"priority": 15}
            self._import_record(external_id, force=force)


class ProductAttributeValueImporter(Component):
    """Import Odoo Attribute Value"""

    _name = "odoo.product.attribute.value.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.attribute.value"

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        record = self.odoo_record
        if attribute_id := record["attribute_id"]:
            self._import_dependency(
                attribute_id[0], "odoo.product.attribute", force=force
            )


class ProductAttributeValueMapper(Component):
    _name = "odoo.product.attribute.value.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.attribute.value"

    direct = [
        ("name", "name"),
        ("numeric_value", "numeric_value"),
    ]

    def get_attribute_id(self, record):
        binder = self.binder_for("odoo.product.attribute")
        local_attribute_id = binder.to_internal(record["attribute_id"][0], unwrap=True)
        return local_attribute_id.id

    @mapping
    def attribute_id(self, record):
        return {"attribute_id": self.get_attribute_id(record)}

    @only_create
    @mapping
    def check_att_value_exists(self, record):
        if not record.get("name"):
            return {}
        lang = self.backend_record.get_default_language_code()
        att_id = self.get_attribute_id(record)
        value_id = (
            self.env["product.attribute.value"]
            .with_context(lang=lang)
            .search(
                [
                    ("attribute_id", "=", att_id),
                    ("name", "=", record.get("name")),
                ],
                limit=1,
            )
        )
        vals = {}
        if value_id:
            vals["odoo_id"] = value_id.id
        return vals

    @mapping
    def html_description(self, record):
        """Sometimes user can edit HTML field with JS editor.
        This may lead to add some old styles from the main instance.
        So we are cleaning the HTML before importing it."""
        vals = {
            "html_description": False,
        }
        if desc := record["html_description"]:
            cleaner = Cleaner(style=True, remove_unknown_tags=False)
            vals["html_description"] = cleaner.clean_html(desc) or ""
        return vals

    @mapping
    def image(self, record):
        vals = {"image": False}
        if image := record.get("image"):
            vals["image"] = image
