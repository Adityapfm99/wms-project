from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestFirstApprovalWizard(models.TransientModel):
    _name = 'purchase.request.first.approval.wizard'
    _description = 'First Approval Signature Wizard'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request", required=True)
    signature = fields.Binary(string="Signature", required=True)

    def action_confirm_signature(self):
        # Check if the signature is provided
        if not self.signature:
            raise UserError("Please provide a signature before confirming.")

        # Capture the first approval signature
        self.purchase_request_id.approval_signature_1 = self.signature
        self.purchase_request_id.approver_id = self.env.user  # Set the first approver

        # If the total cost is greater than 5,000,000, move to 'waiting_approval' state
        if self.purchase_request_id.total_estimated_cost > 5000000:
            self.purchase_request_id.approval_stage = 'waiting_approval'
            self.purchase_request_id.state = 'waiting_approval'
            print("First approval completed. Waiting for second approval.")
        else:
            # If the total cost is below 5,000,000, directly approve
            self.purchase_request_id.approval_stage = 'approved'
            self.purchase_request_id.state = 'approved'
            print("First approval completed, purchase request fully approved (no second approval needed).")

        return {'type': 'ir.actions.act_window_close'}
