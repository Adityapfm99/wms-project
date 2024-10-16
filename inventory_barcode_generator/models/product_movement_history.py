from odoo import models, fields, api
import base64
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm,mm
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageOps
import io
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Table, TableStyle


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
    signature_image = fields.Binary(string="Signature Image")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments", domain=[('res_model', '=', 'product.movement.history')])
    barcode = fields.Char(string="Barcode")
    assignment_id = fields.Many2one('product.user.assignment', string="User Assignment")


    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            movements = self.env['stock.move'].search([
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date),
            ])
            self.product_id = movements.mapped('product_id')

            
    def _generate_signed_pdf(self):
        try:
            # Create a PDF in memory
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            # Company Logo
            if self.env.user.company_id.logo:
                logo_data = base64.b64decode(self.env.user.company_id.logo)
                logo_image = Image.open(io.BytesIO(logo_data))
                logo_buffer = io.BytesIO()
                logo_image.save(logo_buffer, format='PNG')
                p.drawImage(ImageReader(logo_buffer), 1.5 * cm, height - 4 * cm, width=2 * cm, height=2 * cm)

            # Company Header
            company = self.env.user.company_id
            p.setFont("Helvetica-Bold", 14)
            p.drawString(5 * cm, height - 2 * cm, company.name)
            p.setFont("Helvetica", 12)
            p.drawString(5 * cm, height - 2.5 * cm, company.street or '')
            p.drawString(5 * cm, height - 3 * cm, f"{company.city or ''}, {company.state_id.name or ''}, {company.zip or ''}")
            p.drawString(5 * cm, height - 3.5 * cm, company.country_id.name or '')
            p.drawString(5 * cm, height - 4 * cm, f"Phone: {company.phone or ''}")
            p.drawString(5 * cm, height - 4.5 * cm, f"Email: {company.email or ''}")

            # Document Title
            p.setFont("Helvetica-Bold", 16)
            p.drawString(2 * cm, height - 6 * cm, "Signed Movement Asset")

            # Movement Information
            gmt_plus_7 = timezone(timedelta(hours=7))
            current_time = datetime.now(gmt_plus_7).strftime('%Y-%m-%d %H:%M:%S')
            p.setFont("Helvetica", 12)
            p.drawString(2 * cm, height - 7.5 * cm, f"Reference: {self.user_id.name}")
            p.drawString(2 * cm, height - 8 * cm, f"Date: {current_time}")
            p.drawString(2 * cm, height - 8.5 * cm, f"Signed by: {self.env.user.name}")

            # Product Table
            p.setFont("Helvetica-Bold", 12)
            p.drawString(2 * cm, height - 12* cm, "Products:")
            
            
            data = [
                ['Product', 'Quantity', 'Barcode', 'Location'],
                [self.product_id.name, self.quantity, self.barcode or '', self.stock_location_id.name]
            ]
            table = Table(data, colWidths=[6 * cm, 2 * cm, 2 * cm, 4 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            table.wrapOn(p, width, height)
            table.drawOn(p, 2 * cm, height - 14 * cm)

            # Barcode
            
            # if self.barcode:
            #     barcode = code128.Code128(self.barcode, barHeight=20*mm, barWidth=0.5*mm)
            #     barcode.drawOn(p, 2 * cm, height - table_height - 14 * cm)

            # Signature

            if self.signature_image:
                signature_image = base64.b64decode(self.signature_image)
                image = Image.open(io.BytesIO(signature_image)).convert("RGBA")
                bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
                combined = Image.alpha_composite(bg, image)
                combined = combined.convert("RGB")
                image_buffer = io.BytesIO()
                combined.save(image_buffer, format='PNG')
                image_buffer.seek(0)
                p.drawImage(ImageReader(image_buffer), 3 * cm, 1.5 * cm, width=6* cm, height=3 * cm)
                # Add signed by text below the signature
                p.setFont("Helvetica", 10)
                p.drawString(3 * cm, 1.5 * cm, f"Signed by: {self.env.user.name}")
            else:
                print("No signature image found.")

            p.save()
            pdf_data = buffer.getvalue()
            buffer.close()

            attachment = self.env['ir.attachment'].create({
                'name': f'{self.env.user.name}_signed_asset_asssignment.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_data),
                'res_model': 'product.movement.history',
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

        except Exception as e:
            print(f"Error generating and attaching PDF: {e}")
            raise KeyError(f"Error generating and attaching PDF: {e}")

        return attachment