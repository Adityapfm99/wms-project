from odoo import models, fields

class Livestock(models.Model):
    _name = 'farming_management.livestock'
    _description = 'Livestock Management'

    name = fields.Char(string='Animal ID', required=True)
    breed = fields.Char(string='Breed')
    age = fields.Integer(string='Age')
    health_status = fields.Selection([('healthy', 'Healthy'), ('sick', 'Sick')], string='Health Status')
    farm_id = fields.Many2one('farming_management.farm', string='Farm')
