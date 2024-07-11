from odoo import models, fields, api
import base64
from io import BytesIO

from odoo.exceptions import UserError

class ProductUserAssignment(models.Model):
    _name = 'product.user.assignment'
    _description = 'Product User Assignment'

    product_ids = fields.Many2many('product.product', string='Products')
    barcode = fields.Char(string='Barcode')
    user_id = fields.Many2one('res.users', string='User', required=True)
    assign_date = fields.Datetime(string='Assign Date', default=fields.Datetime.now)
    signature = fields.Binary(string='Signature')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
    ], string='Status', default='draft')
    stock_location_ids = fields.Many2many(related='user_id.stock_location_ids', string='Stock Locations', readonly=True)

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if self.barcode:
            product = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
            if product:
                if product not in self.product_ids:
                    self.product_ids = [(4, product.id)]
                self.barcode = False
            else:
                raise UserError('No product found with this barcode.')
            
    def action_sign(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Product Assignment',
            'res_model': 'product.user.assignment',
            'view_mode': 'form',
            'view_id': self.env.ref('inventory_barcode_generator.view_product_user_assignment_sign_form').id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    def action_confirm_signature(self):
        if not self.signature:
            raise KeyError("Please provide a signature before confirming...")
        
        self.state = 'signed'

        for product in self.product_ids:
            # Find the latest history record for the product and update its end_date
            previous_history = self.env['product.movement.history'].search([
                ('product_id', '=', product.id),
                ('end_date', '=', False)
            ], order='move_date desc', limit=1)
            
            if previous_history:
                previous_history.end_date = self.assign_date
            
            # Create product movement history
            self.env['product.movement.history'].create({
                'product_id': product.id,
                'user_id': self.user_id.id,
                'move_date': self.assign_date,
                'start_date': self.assign_date,
                'end_date': None,
                'stock_location_id': self.env.user.stock_location_ids[:1].id if self.env.user.stock_location_ids else False,
                'quantity': 1,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Product assignment signed successfully.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
