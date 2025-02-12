# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from lxml.html.clean import Cleaner

_logger = logging.getLogger(__name__)


class ProductAttributeImporter(Component):
    """Import Odoo UOM"""

    _name = "odoo.product.attribute.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.attribute"

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        if attr_group_id := self.odoo_record["attribute_group_id"]:
            self._import_dependency(
                attr_group_id[0],
                "odoo.product.attribute.group",
                force=force,
            )


class ProductAttributeMapper(Component):
    _name = "odoo.product.attribute.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.attribute"

    direct = [
        ("name", "name"),
        ("create_variant", "create_variant"),
        ("allow_filling", "allow_filling"),
        ("visibility", "visibility"),
    ]

    @only_create
    @mapping
    def check_att_exists(self, record):
        domain = [("name", "=", record["name"])]
        if create_variant := record.get("create_variant"):
            domain.append(("create_variant", "=", create_variant))
        att_id = self.env["product.attribute"].search(domain, limit=1)
        res = {}
        if att_id:
            res.update({"odoo_id": att_id.id})
        return res

    @mapping
    def create_variant(self, record):
        res = {"create_variant": "no_variant"}
        if record.get("create_variant") == "always":
            res.update(create_variant="always")
        return res

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
    def attribute_group_id(self, record):
        vals = {"attribute_group_id": False}
        if group_id := record.get("attribute_group_id"):
            binder = self.binder_for("odoo.product.attribute.group")
            group = binder.to_internal(group_id[0], unwrap=True)
            vals["attribute_group_id"] = group.id
        return vals
