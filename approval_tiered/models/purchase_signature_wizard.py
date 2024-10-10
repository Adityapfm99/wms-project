from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestSignatureWizard(models.TransientModel):
    _name = 'purchase.request.signature.wizard'
    _description = 'Purchase Request Signature Wizard'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request", required=True)
    signature = fields.Binary(string="Signature", required=True)

    def action_confirm_signature(self):
        print("============signature")
        if not self.signature:
            raise UserError("Please provide a signature before confirming.")
        
        # Check the current approval stage and assign signatures accordingly
        if self.purchase_request_id.approval_stage == 'one_approval':
            self.purchase_request_id.approval_signature_1 = self.signature
            self.purchase_request_id.approver_id = self.env.user  # Set the first approver

            # If total cost requires two approvals, trigger the second approver's wizard
            if self.purchase_request_id.total_estimated_cost > 5000000:
                self.purchase_request_id.approval_stage = 'two_approvals'

                # Launch the second approval wizard for the second approver
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Second Approval with Signature'),
                    'res_model': 'purchase.request.signature.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_purchase_request_id': self.purchase_request_id.id,
                        'default_stage': 'two_approvals'
                    },
                }
            else:
                # If only one approval is needed, mark as fully approved
                self.purchase_request_id.approval_stage = 'approved'
                self.purchase_request_id.state = 'approved'

        elif self.purchase_request_id.approval_stage == 'two_approvals':
            # Ensure that the first approval has been completed
            print(f"First approval signature: {self.purchase_request_id.approval_signature_1}")
            print(f"Second approval signature before assignment: {self.signature}")

            if not self.purchase_request_id.approval_signature_1:
                raise UserError('First approval must be completed before second approval.')

            # Ensure that the second approver is different from the first approver
            if self.purchase_request_id.approver_id == self.env.user:
                raise UserError('The second approval must be completed by a different user.')

            # Capture the second approval signature and mark the second approver
            self.purchase_request_id.approval_signature_2 = self.signature
            print(f"Second approval signature after assignment: {self.purchase_request_id.approval_signature_2}")
            self.purchase_request_id.second_approver_id = self.env.user  # Set the second approver

            # Mark the request as fully approved
            self.purchase_request_id.approval_stage = 'approved'
            self.purchase_request_id.state = 'approved'