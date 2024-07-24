from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    agriculture_role = fields.Selection([
        ('manager', 'Manager'),
        ('officer', 'Officer')
    ], string='Agriculture Role')
