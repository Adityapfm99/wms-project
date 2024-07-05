from odoo import models, fields, api
import base64
import sys
sys.path.append('/cloudclusters/odoo/odoo/venv/lib/python3.10/site-packages')
import barcode
import os
from barcode.writer import ImageWriter
from io import BytesIO
from reportlab.lib.pagesizes import A7
from reportlab.pdfgen import canvas
import tempfile
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_image = fields.Binary("Barcode Image", compute='_generate_barcode')

    @api.depends('barcode')
    def _generate_barcode(self):
        for record in self:
            if record.barcode:
                if len(record.barcode) != 13 or not record.barcode.isdigit():
                    _logger.error("Barcode must be exactly 13 digits long.")
                    raise UserError("Barcode must be exactly 13 digits long and numeric.")
                
                EAN13 = barcode.get_barcode_class('ean13')
                ean13 = EAN13(record.barcode, writer=ImageWriter())
                buffer = BytesIO()
                ean13.write(buffer)
                record.barcode_image = base64.b64encode(buffer.getvalue())
            else:
                record.barcode_image = False
                
    def action_print_barcode(self):
        _logger.info("Printing barcode for product: %s", self.name)
        for record in self:
            if record.barcode:
                data = {'model': 'product.template', 'ids': [record.id], 'form': {'doc': record.read()[0]}}
                # _logger.info("Report data: %s", data) 
                return {
                    'type': 'ir.actions.report',
                    'report_name': 'inventory_barcode_generator.report_template',
                    'report_type': 'qweb-pdf',
                    'context': {'active_id': record.id, 'active_model': 'product.template'},
                    'data': data,
                }
            else:
                _logger.error("No barcode available to print for product: %s", self.name)
                raise UserError("No barcode available to print.")

    def action_open_barcode_preview(self):
        return {
            'name': 'Barcode Preview',
            'type': 'ir.actions.act_window',
            'res_model': 'barcode.preview.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_id': self.id},
        }