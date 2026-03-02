from odoo import models, fields

class DkmsVersion(models.Model):
    _name = "dkms.version"
    _description = "Document Version"

    document_id = fields.Many2one("dkms.document", required=True, ondelete="cascade")
    content = fields.Html()
    file = fields.Binary()
    version = fields.Char(required=True)
    create_date = fields.Datetime(readonly=True)