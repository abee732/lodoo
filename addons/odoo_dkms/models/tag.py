from odoo import models, fields

class DkmsTag(models.Model):
    _name = "dkms.tag"
    _description = "Knowledge Tag"

    name = fields.Char(required=True)
    color = fields.Integer()