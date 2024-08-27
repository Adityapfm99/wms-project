from odoo import models, fields

class CropRawMaterial(models.Model):
    _name = 'farming_management.crop.raw.material'
    _description = "Crop's Raw Material"

    crop_id = fields.Many2one('farming_management.crop', string='Crop')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
