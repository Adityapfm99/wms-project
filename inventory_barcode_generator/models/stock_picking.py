from odoo import models, fields, api
import base64
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import A4,landscape
from odoo.exceptions import UserError
from reportlab.lib.units import cm
from datetime import datetime, timedelta, timezone
from PIL import Image,ImageOps
import io
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    signature_image = fields.Binary(string="Signature Image")

    def set_signature(self, signature):
        self.signature_image = signature

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.state == 'done':
                try:
                    attachment = self._generate_signed_pdf()
                    # Post a message in the chatter
                    self.message_post(
                        body="Signed picking receipt generated.",
                        attachment_ids=[attachment.id]
                    )
                except Exception as e:
                    print(f"Error generating PDF: {e}")
        return res
    

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
            p.drawString(2 * cm, height - 6 * cm, "Signed Picking Receipt")

            # Picking Information
            gmt_plus_7 = timezone(timedelta(hours=7))
            current_time = datetime.now(gmt_plus_7).strftime('%Y-%m-%d %H:%M:%S')
            p.setFont("Helvetica", 12)
            p.drawString(2 * cm, height - 7.5 * cm, f"Picking: {self.name}")
            p.drawString(2 * cm, height - 8 * cm, f"Date: {current_time}")

            # Origin and Destination Locations
            p.drawString(2 * cm, height - 10 * cm, f"Origin: {self.location_id.complete_name}")
            p.drawString(2 * cm, height - 10.5 * cm, f"Destination: {self.location_dest_id.complete_name}")

            # Product List in a Table
            p.setFont("Helvetica-Bold", 12)
            p.drawString(2 * cm, height - 12 * cm, "Products:")

            data = [["Product", "Quantity"]]
            for line in self.move_line_ids:
                data.append([f"{line.product_id.default_code or ''} {line.product_id.name}", f"{line.quantity} {line.product_id.uom_id.name}"])

            table = Table(data, colWidths=[10 * cm, 4 * cm])
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

            # Signature
            p.setFont("Helvetica-Bold", 12)
            p.drawString(2 * cm, 2 * cm, "Signature")
            p.line(5 * cm, 1.9 * cm, 10 * cm, 1.9 * cm)
            # Assuming the signature image is stored in a field called 'signature_image'
            if self.signature_image:
                # Convert base64 image data to an image
                signature_image = base64.b64decode(self.signature_image)
                image = Image.open(io.BytesIO(signature_image)).convert("RGBA")

                # Create a white background
                bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
                combined = Image.alpha_composite(bg, image)

                # Convert combined image to RGB
                combined = combined.convert("RGB")

                # Save to buffer
                image_buffer = io.BytesIO()
                combined.save(image_buffer, format='PNG')
                image_buffer.seek(0)

                p.drawImage(ImageReader(image_buffer), 5 * cm, 1.5 * cm, width=6* cm, height=3 * cm)
                # Add signed by text below the signature
                p.setFont("Helvetica", 10)
                p.drawString(6 * cm, 1.5 * cm, f"Signed by: {self.env.user.name}")
            else:
                print("No signature image found.")

            p.save()

            # Get the PDF data
            pdf_data = buffer.getvalue()
            buffer.close()

            # Save the PDF as an attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'{self.name}_signed_receipt.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_data),
                'res_model': 'stock.picking',
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

        except Exception as e:
            print(f"Error generating and attaching PDF: {e}")
            raise UserError(f"Error generating and attaching PDF: {e}")

        return attachment
