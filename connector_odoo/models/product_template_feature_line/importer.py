# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class ProductTemlateFeatureLineImporter(Component):
    """Import Odoo Product Feature Line"""

    _name = "odoo.product.template.feature.line.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.product.template.feature.line"

    # def _get_binding2(self, binding):
    #     if binding:
    #         return binding
    #     res = super()._get_binding2(binding)
    #     if not res:
    #         record = self.odoo_record
    #         mapper = self.component(usage="import.mapper")
    #         attr_line = self.env["product.template.feature.line"].search(
    #             [
    #                 ("product_tmpl_id", "=", mapper._get_product_tmpl_id(record)),
    #                 ("feature_id", "=", mapper._get_feature_id(record)),
    #                 ("value_ids", "=", mapper._get_feature_value_id(record)),
    #             ], limit=1
    #         )
    #         attr_line
    #         # res = {}
    #         # if len(attr_line) > 0:
    #         #     res.update({"odoo_id": attr_line.id})
    #     return res

    # def _import_dependencies(self, force=False):
    #     """Import the dependencies for the record"""
    #     record = self.odoo_record
    #     self._import_dependency(
    #         record.feature_id.id, "odoo.product.feature", force=force
    #     )



class ProductTemplateFeatureLineMapper(Component):
    _name = "odoo.product.template.feature.line.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.product.template.feature.line"

    # Todo: altınkaya fields. check if needed
    # direct = [
    #     ("attr_type", "attr_type"),
    #     ("attr_base_price", "attr_base_price"),
    #     ("required", "required"),
    #     ("use_in_pricing", "use_in_pricing"),
    # ]

    def _get_feature_id(self, record):
        binder = self.binder_for("odoo.product.attribute")
        return binder.to_internal(record.feature_id.id, unwrap=True).id

    def _get_feature_value_id(self, record):
        binder = self.binder_for("odoo.product.attribute.value")
        vals = []
        for value in record.value_ids:
            local_feature_value_id = binder.to_internal(value.id, unwrap=True).id
            vals.append(local_feature_value_id)
        return vals

    @mapping
    def feature_id(self, record):
        return {"feature_id": self._get_feature_id(record)}

    @mapping
    def feature_value_id(self, record):
        return {"value_ids": [(6, 0, self._get_feature_value_id(record))]}

    def _get_product_tmpl_id(self, record):
        binder = self.binder_for("odoo.product.template")
        return binder.to_internal(record.product_tmpl_id.id, unwrap=True).id

    @only_create
    @mapping
    def product_tmpl_id(self, record):
        return {"product_tmpl_id": self._get_product_tmpl_id(record)}
