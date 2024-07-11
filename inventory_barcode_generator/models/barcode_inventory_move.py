import logging

_logger = logging.getLogger(__name__)

from odoo import models, fields, api
from odoo.exceptions import UserError

class BarcodeInventoryMove(models.TransientModel):
    _name = 'barcode.inventory.move'
    _description = 'Barcode Inventory Move'

    barcode = fields.Char(string="Barcode")
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    location_id = fields.Many2one('stock.location', string="Origin Warehouse",store=True)
    location_dest_id = fields.Many2one('stock.location', string="Destination Warehouse")
    move_line_ids = fields.One2many('barcode.inventory.move.line', 'barcode_inventory_move_id', string='Products')
    move_type = fields.Selection([('receipt', 'Receipt'), ('delivery', 'Delivery')], string="Move Type", required=True, default='receipt')


    @api.onchange('barcode')
    def _onchange_barcode(self):

        if self.barcode:
            _logger.info(f"Searching for product with barcode: {self.barcode}")
            product = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
            _logger.info(f"Product search result: {product.id if product else 'None'}")
            if product:
                _logger.info(f"Product found: {product.name}")
                source_location = self._get_latest_product_location(product.id) if self.move_type == 'receipt' else self.location_id.id if self.location_id else False

                new_line = {
                    'product_id': product.id,
                    'quantity': 1.0,  
                    'location_id': source_location,
                    'location_dest_id': self.location_dest_id.id if self.location_dest_id else False,
                    'barcode': self.barcode
                }
                self.update({'move_line_ids': [(0, 0, new_line)]})
                self.barcode = ''
            else:
                _logger.info("No product found")
                return {
                    'warning': {
                        'title': "No Product Found",
                        'message': "No product found with the given barcode."
                    }
                }

    @api.onchange('move_type')
    def _onchange_move_type(self):
        if self.move_type == 'delivery':
            self.location_id = self.env.user.stock_location_ids[:1].id if self.env.user.stock_location_ids else False
        else:
            self.location_id = False
        if self.move_type =='receipt':
            self.location_dest_id = self.env.user.stock_location_ids[:1].id if self.env.user.stock_location_ids else False
            
        else:
            self.location_dest_id = False

    def _get_latest_product_location(self, product_id):
        stock_quant = self.env['stock.quant'].search([('product_id', '=', product_id)], limit=1, order='in_date desc')
        return stock_quant.location_id if stock_quant else False
    
    def action_move_inventory1(self):
        if not self.location_dest_id:
            raise UserError("Please select a Destination location first.")
        if not self.location_id and self.move_type in ['delivery', 'receipt']:
            raise UserError("Please select a Origin location first.")

        if not self.move_line_ids:
            raise UserError("No products to move.")

        picking_type = self.env.ref('stock.picking_type_internal')
        if self.move_type == 'receipt':
            picking_type = self.env.ref('stock.picking_type_in')
        elif self.move_type == 'delivery':
            picking_type = self.env.ref('stock.picking_type_out')
        elif self.move_type == 'transfer':
            picking_type = self.env.ref('stock.picking_type_internal')

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.location_id.id if self.move_type in ['delivery', 'transfer'] else self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.location_dest_id.id,
        })

        _logger.info(f"Created stock picking: {picking.name}")

        for line in self.move_line_ids:
            available_qty = self.env['stock.quant'].read_group(
                [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)],
                ['quantity:sum'],
                ['product_id', 'location_id']
            )

            if available_qty and available_qty[0]['quantity'] < line.quantity:
                raise UserError(f"Not enough quantity of {line.product_id.name} in source location {line.location_id.display_name}.")

        # Create stock moves
        for line in self.move_line_ids:
            move = self.env['stock.move'].create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'location_id': line.location_id.id if self.move_type in ['delivery', 'transfer'] else self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': line.location_dest_id.id,
                'picking_id': picking.id,
            })
            _logger.info(f"Created stock move: {move.name}")

        picking.action_confirm()
        picking.action_assign()

        for move in picking.move_ids_without_package:
            move.quantity = move.product_uom_qty

        picking.button_validate()

        _logger.info(f"Stock picking {picking.name} validated")
        
        
        if not self.location_dest_id:
            raise UserError("Please select a destination location first.")
        if not self.location_id:
            raise UserError("Please select a Source location first.")

        if not self.move_line_ids:
            raise UserError("No products to move.")

        picking_type_internal = self.env.ref('stock.picking_type_internal')
        picking_type = picking_type_internal

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.location_id.id if self.move_type == 'delivery' else self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.location_dest_id.id,
        })

        _logger.info(f"Created stock picking: {picking.name}")

        for line in self.move_line_ids:
            available_qty = self.env['stock.quant'].read_group(
                [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)],
                ['quantity:sum'],
                ['product_id', 'location_id']
            )

            if available_qty and available_qty[0]['quantity'] < line.quantity:
                raise UserError(f"Not enough quantity of {line.product_id.name} in source location {line.location_id.display_name}.")

        # Create stock moves
        for line in self.move_line_ids:
            move = self.env['stock.move'].create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.location_id.id if self.move_type == 'delivery' else self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': line.location_dest_id.id,
                'picking_id': picking.id,
            })
            _logger.info(f"Created stock move: {move.name}")

        picking.action_confirm()
        picking.action_assign()

        for move in picking.move_ids:
            move_line = self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'quantity': move.product_uom_qty,
            })

        _logger.info(f"Move Line Created")

        picking.button_validate()

        _logger.info(f"Stock picking {picking.name} validated")
        
        return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'Stock picking Validated Successfully.',
            'type': 'success', 
            'sticky': False,
            'next': {'type': 'ir.actions.act_window_close'}
        },
    }

    