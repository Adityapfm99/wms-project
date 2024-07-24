
from odoo import models, fields, api

class BillOfMaterials(models.Model):
    _name = 'farming_management.bom'
    _description = 'Bill of Materials'

    name = fields.Char(string='BOM Name', required=True)
    crop_id = fields.Many2one('farming_management.crop', string='Crop', required=True)
    product_ids = fields.One2many('farming_management.bom.line', 'bom_id', string='Products')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost')

    @api.depends('product_ids', 'product_ids.cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = sum(line.cost for line in record.product_ids)
