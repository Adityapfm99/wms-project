from odoo import models, fields

class Equipment(models.Model):
    _name = 'farming_management.equipment'
    _description = 'Equipment Management'

    name = fields.Char(string='Equipment Name', required=True)
    type = fields.Selection([('tractor', 'Tractor'), ('plow', 'Plow')], string='Type')
    maintenance_date = fields.Date(string='Next Maintenance Date')
    farm_id = fields.Many2one('farming_management.farm', string='Farm')
