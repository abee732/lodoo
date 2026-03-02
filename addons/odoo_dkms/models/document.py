from odoo import models, fields, api

class DkmsDocument(models.Model):
    _name = "dkms.document"
    _description = "Knowledge Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    folder_id = fields.Many2one("dkms.folder", tracking=True)

    content = fields.Html()
    file = fields.Binary()
    filename = fields.Char()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], default='draft', tracking=True)

    tag_ids = fields.Many2many("dkms.tag")
    version_ids = fields.One2many("dkms.version", "document_id")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self.env["dkms.version"].create({
                "document_id": rec.id,
                "content": rec.content or "",
                "version": "v1.0"
            })
        return records

    def action_submit_review(self):
        self.state = "review"

    def action_approve(self):
        self.state = "approved"

    def action_publish(self):
        self.state = "published"

    def action_archive(self):
        self.state = "archived"