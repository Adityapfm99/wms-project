from odoo import models, fields, api

class CropDashboard(models.Model):
    _name = 'farming_management.crop.dashboard'
    _description = 'Crop Dashboard'

    name = fields.Char(string='Crop Name')
    farm_id = fields.Many2one('farming_management.farm', string='Farm')
    planting_date = fields.Date(string='Planting Date')
    days_since_planting = fields.Integer(string='Days Since Planting', compute='_compute_days_since_planting')

    @api.depends('planting_date')
    def _compute_days_since_planting(self):
        for record in self:
            if record.planting_date:
                delta = fields.Date.today() - record.planting_date
                record.days_since_planting = delta.days
            else:
                record.days_since_planting = 0
