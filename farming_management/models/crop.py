from odoo import models, fields

class Crop(models.Model):
    _name = 'farming_management.crop'
    _description = 'Crop Management'

    name = fields.Char(string='Crop Name', required=True)
    farm_id = fields.Many2one('farming_management.farm', string='Farm', required=True)
    planting_date = fields.Date(string='Planting Date')
    harvest_date = fields.Date(string='Harvest Date')
    quantity = fields.Float(string='Quantity')
    period_to_produce = fields.Integer(string='Period to Produce Crop (Months)', required=True)
    season = fields.Selection([
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter')
    ], string='Crop Season', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Crop Warehouse')
    stock_location_id = fields.Many2one('stock.location', string='Crop Stock Location')
    raw_material_ids = fields.One2many('farming_management.crop.raw.material', 'crop_id', string="Crop's Raw Materials")
    # Add any other necessary fields
