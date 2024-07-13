from odoo import models, fields

class BarcodeInventoryMoveLine(models.TransientModel):
    _name = 'barcode.inventory.move.line'
    _description = 'Barcode Inventory Move Line'

    barcode_inventory_move_id = fields.Many2one('barcode.inventory.move', string='Barcode Inventory Move')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    location_id = fields.Many2one('stock.location', string='Origin Warehouse')
    location_dest_id = fields.Many2one('stock.location', string='Destination Warehouse', required=True)
    barcode = fields.Char(string='Barcode')
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)
