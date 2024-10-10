from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestCreationSignatureWizard(models.TransientModel):
    _name = 'purchase.request.creation.signature.wizard'
    _description = 'Purchase Request Creation Signature Wizard'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request", required=True)
    signature = fields.Binary(string="Signature", required=True)
    

    def action_confirm_signature(self):
        if not self.signature:
            raise UserError("Please provide a signature before confirming.")
        
        # Capture the signature and save it to the purchase request
        self.purchase_request_id.approval_signature_1 = self.signature
        self.purchase_request_id.approver_id = self.env.user

        # After signing, mark the state as "one_approval" for first approval
        self.purchase_request_id.state = 'one_approval'
        return {'type': 'ir.actions.act_window_close'}
