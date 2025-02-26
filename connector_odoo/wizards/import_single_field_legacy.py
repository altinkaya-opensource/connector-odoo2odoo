# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models, api


class ImportSingleFieldLegacyWizard(models.TransientModel):
    _name = "import.single.field.legacy.wizard"
    _description = "Import Single Field Legacy Wizard"

    def _get_default_backend(self):
        return self.env["odoo.backend"].search([], limit=1).id

    backend_id = fields.Many2one(
        "odoo.backend", required=True, default=_get_default_backend
    )
    model_id = fields.Many2one(
        "ir.model", required=True, domain="[('model', 'like', 'odoo.%')]"
    )
    field_name = fields.Char(required=True)
    to_field_name = fields.Char(required=True)
    many2one_import = fields.Boolean(default=False)
    many2one_related_model = fields.Char()

    def action_import(self):
        self.ensure_one()
        self.with_delay()._import_single_field()

    def _import_single_field(self):
        connection = self.backend_id.get_connection()
        imported_records = self.env[self.model_id.model].search(
            [("backend_id", "=", self.backend_id.id)]
        )
        domain = [("id", "in", imported_records.mapped("external_id"))]
        if hasattr(self.model_id, "active"):
            domain += [
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
        external_records = connection.search(
            model=self.model_id.model.lstrip("odoo."),
            domain=domain,
            fields=[self.field_name],
        )
        record_dict = {rec.external_id: rec for rec in imported_records}
        external_records = {rec["id"]: rec for rec in external_records}
        if self.many2one_import:
            binding_model = self.env["odoo.%s" % self.many2one_related_model]
        else:
            binding_model = self.env[self.model_id.model]
        for record_external_id, record in record_dict.items():
            data = external_records.get(record_external_id)
            if data and (external_field := data.get(self.field_name)):
                if self.many2one_import:
                    related_model = binding_model.search(
                        [("external_id", "=", external_field[0])]
                    )
                    if related_model:
                        record.write({self.to_field_name: related_model.odoo_id.id})
                else:
                    record.write({self.to_field_name: external_field})

        return True
