from odoo.addons.component.core import Component


class CustomizationDepartmentBatchImporter(Component):
    _name = "odoo.customization.department.batch.importer"
    _inherit = "odoo.delayed.batch.importer"
    _apply_on = ["odoo.customization.department"]


class CustomizationDepartmentImporter(Component):
    """Import Odoo Customization Department"""

    _name = "odoo.customization.department.importer"
    _inherit = "odoo.importer"
    _apply_on = "odoo.customization.department"


class CustomizationDepartmentMapper(Component):
    _name = "odoo.customization.department.mapper"
    _inherit = "odoo.import.mapper"
    _apply_on = "odoo.customization.department"

    direct = [
        ("name", "name"),
        ("code", "code"),
        ("html_description", "html_description"),
        ("price_table", "price_table"),
    ]
