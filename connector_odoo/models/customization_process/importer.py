import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class CustomizationProcessBatchImporter(Component):
    _name = "odoo.customization.process.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.customization.process"]


class CustomizationProcessImporter(Component):
    """Import Odoo Customization Process"""

    _name = "odoo.customization.process.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.customization.process"

    def _import_dependencies(self, force=False):
        department_id = self.odoo_record.get("department_id")
        if department_id:
            self._import_dependency(department_id[0], "odoo.customization.department", force=force)


class CustomizationProcessMapper(Component):
    _name = "odoo.customization.process.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.customization.process"

    direct = [
        ("name", "name"),
        ("factor_a", "factor_a"),
        ("factor_b", "factor_b"),
        ("x_name", "x_name"),
        ("y_name", "y_name"),
        ("formula", "formula"),
        ("html_description", "html_description")
    ]

    @mapping
    def department_id(self, record):
        vals = {"department_id": False}

        if record.get("department_id"):
            binder = self.binder_for("odoo.customization.department")
            department = binder.to_internal(record.get("department_id")[0], unwrap=True)
            vals["department_id"] = department.id

        return vals
