from odoo import models, fields

class DkmsFolder(models.Model):
    _name = "dkms.folder"
    _description = "Knowledge Folder"
    _parent_store = True

    name = fields.Char(required=True)
    parent_id = fields.Many2one("dkms.folder", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("dkms.folder", "parent_id")

    document_ids = fields.One2many("dkms.document", "folder_id")
    color = fields.Integer()