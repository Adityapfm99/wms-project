from odoo import models, fields

class Farm(models.Model):
    _name = 'farming_management.farm'
    _description = 'Farm Management'
    
    name = fields.Char(string='Farm Name', required=True)
    location = fields.Char(string='Location')
    area = fields.Float(string='Area (hectares)')
    crop_ids = fields.One2many('farming_management.crop', 'farm_id', string='Crops')
