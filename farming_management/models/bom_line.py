from odoo import models, fields, api

class BillOfMaterialsLine(models.Model):
    _name = 'farming_management.bom.line'
    _description = 'Bill of Materials Line'

    bom_id = fields.Many2one('farming_management.bom', string='Bill of Materials')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    cost = fields.Float(string='Cost', compute='_compute_cost')

    @api.depends('product_id', 'quantity')
    def _compute_cost(self):
        for line in self:
            line.cost = line.product_id.standard_price * line.quantity
