from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestFirstApprovalWizard(models.TransientModel):
    _name = 'purchase.request.second.approval.wizard'
    _description = 'Second Approval Signature Wizard'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request", required=True)
    signature = fields.Binary(string="Signature", required=True)

    def action_confirm_signature(self):
        if not self.signature:
            raise UserError("Please provide a signature before confirming.")
        
        # Ensure only the second signature is updated
        if self.purchase_request_id.approval_signature_1:
            print("First approval already exists")
        
        # Capture the second approval signature, leaving the first one intact
        self.purchase_request_id.approval_signature_2 = self.signature
        self.purchase_request_id.second_approver_id = self.env.user

        # Set the approval_stage to 'approved'
        self.purchase_request_id.approval_stage = 'approved'
        self.purchase_request_id.state = 'approved'

        return {'type': 'ir.actions.act_window_close'}
