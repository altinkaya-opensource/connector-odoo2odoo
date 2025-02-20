# Copyright 2013-2017 Camptocamp SA
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError
from lxml.html.clean import Cleaner

_logger = logging.getLogger(__name__)


class ProductCategoryBatchImporter(Component):
    """Import the Odoo Product Categories.

    For every product category in the list, a delayed job is created.
    A priority is set on the jobs according to their level to rise the
    chance to have the top level categories imported first.
    """

    _name = "odoo.product.category.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.product.category"]

    def run(self, domain=None, force=False):
        """Run the synchronization"""

        updated_ids = self.backend_adapter.search(domain)
        _logger.info(
            "search for odoo product categories %s returned %s items",
            domain,
            len(updated_ids),
        )
        for cat in updated_ids:
            self._import_record(cat, force=force)


class ProductCategoryImporter(Component):
    _name = "odoo.product.category.importer"
    _inherit = "odoo.importer"
    _apply_on = ["odoo.product.category"]

    def _import_dependencies(self, force=False):
        """Import the dependencies for the record"""
        record = self.odoo_record
        # import parent category
        # the root category has a 0 parent_id
        if parent := record["parent_id"]:
            self._import_dependency(parent[0], self.model, force=force)
        if feature_icons := record["feature_icon_ids"]:
            for feature_icon in feature_icons:
                self._import_dependency(feature_icon, "odoo.feature.icon", force=force)

        if catalog_attribute_lines := record["catalog_attribute_lines"]:
            for table_attr_line in catalog_attribute_lines:
                self._import_dependency(
                    table_attr_line,
                    "odoo.product.category.table.attribute.lines",
                    force=force,
                )

    def _get_public_category(self, record):
        return self.env["product.public.category"].search(
            [("origin_categ_id", "=", record.id)], limit=1
        )

    def _after_import(self, binding, force=False):
        """Hook called at the end of the import"""
        self._sync_public_category(binding)
        binding._parent_store_compute()
        return super()._after_import(binding, force)

    def _translate_fields(self, binding):
        """
        Translate the public categories name of the binding manually.
        """
        res = super()._translate_fields(binding)
        if res:
            public_categ_id = self._get_public_category(binding.odoo_id)
            translated_fields = self.odoo_record.get("translated_fields")
            if public_categ_id and translated_fields:
                for lang, val in translated_fields["name_translatable"].items():
                    public_categ_id.with_context(lang=lang).write({"name": val})
        return res

    def _sync_public_category(self, binding):
        """Create a public category for the binding"""
        categ_id = binding.odoo_id

        public_categ_id = self._get_public_category(categ_id)
        parent_id = self.env["product.public.category"].search(
            [
                ("origin_categ_id", "!=", False),
                ("origin_categ_id", "=", categ_id.parent_id.id),
            ],
            limit=1,
        )

        vals = {
            "name": self.odoo_record["name_translatable"],
            "sequence": self.odoo_record["sequence"],
            "origin_categ_id": categ_id.id,
            "website_id": self.env.user.company_id.website_id.id,
            "parent_id": parent_id.id or False,
        }

        if not public_categ_id:
            public_categ_id = self.env["product.public.category"].create(vals)
            _logger.info(
                "created public category %s for odoo product category %s",
                public_categ_id,
                binding,
            )
        else:
            public_categ_id.write(vals)
            _logger.info(
                "writed public category %s for odoo product category %s",
                public_categ_id,
                binding,
            )
        public_categ_id._compute_product_tmpls()
        public_categ_id._parent_store_compute()
        return True


class ProductCategoryImportMapper(Component):
    _name = "odoo.product.category.import.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.category"

    direct = [
        ("name_translatable", "name_translatable"),
        ("name", "name"),
        ("sequence", "sequence"),
        ("is_published", "is_published"),
        ("pricelist_discount_scales", "pricelist_discount_scales"),
        ("show_in_pricelist", "show_in_pricelist"),
        ("ecommerce_image", "ecommerce_image"),
        ("show_all_products", "show_all_products"),
        ("show_in_catalog", "show_in_catalog"),
        ("catalog_sequence", "catalog_sequence"),
        ("pre_pdf_catalog", "pre_pdf_catalog"),
        ("post_pdf_catalog", "post_pdf_catalog"),
        ("catalog_main_image", "catalog_main_image"),
        ("catalog_technical_drawing_image", "catalog_technical_drawing_image"),
    ]

    @mapping
    def feature_icon_ids(self, record):
        vals = {"feature_icon_ids": False}
        if feature_icons := record.get("feature_icon_ids"):
            icon_ids = []
            binder = self.binder_for("odoo.feature.icon")
            for icon in feature_icons:
                local_icon_id = binder.to_internal(icon, unwrap=True)
                if not local_icon_id:
                    raise MappingError(
                        "The feature icon with Odoo id %s is not imported." % icon.id
                    )
                icon_ids.append(local_icon_id.id)

            vals["feature_icon_ids"] = [(6, 0, icon_ids)]
        return vals

    @mapping
    def catalog_attribute_lines(self, record):
        vals = {"catalog_attribute_lines": False}
        if table_attr_lines := record.get("catalog_attribute_lines"):
            line_ids = []
            binder = self.binder_for("odoo.product.category.table.attribute.lines")
            for line in table_attr_lines:
                local_line_id = binder.to_internal(line, unwrap=True)
                if not local_line_id:
                    raise MappingError(
                        "The table attribute line with Odoo id %s is not imported."
                        % line
                    )
                line_ids.append(local_line_id.id)

            vals["catalog_attribute_lines"] = [(6, 0, line_ids)]
        return vals

    @mapping
    def catalog_description(self, record):
        """Sometimes user can edit HTML field with JS editor.
        This may lead to add some old styles from the main instance.
        So we are cleaning the HTML before importing it."""
        vals = {
            "catalog_description": False,
        }
        if desc := record["catalog_description"]:
            cleaner = Cleaner(style=True, remove_unknown_tags=False)
            vals["catalog_description"] = cleaner.clean_html(desc) or ""
        return vals

    @mapping
    def parent_id(self, record):
        vals = {"parent_id": False, "odoo_parent_id": False}
        if not (parent := record.get("parent_id")):
            return vals
        binder = self.binder_for()
        parent_binding = binder.to_internal(parent[0])

        if not parent_binding:
            raise MappingError(
                "The product category with "
                "Odoo id %s is not imported." % record.parent_id.id
            )

        parent = parent_binding.odoo_id
        vals.update({"parent_id": parent.id, "odoo_parent_id": parent_binding.id})
        return vals
