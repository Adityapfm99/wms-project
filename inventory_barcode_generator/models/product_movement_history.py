from odoo import models, fields, api

class ProductMovementHistory(models.Model):
    _name = 'product.movement.history'
    _description = 'Product Movement History'

    product_id = fields.Many2one('product.product', string='Asset', required=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    stock_location_id = fields.Many2one('stock.location', string='Asset Location', required=True)
    move_date = fields.Datetime(string='Movement Date', required=True, default=fields.Datetime.now)
    quantity = fields.Float(string='Quantity')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
   

    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            movements = self.env['stock.move'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
            ])
            self.product_id = movements.mapped('product_id')
