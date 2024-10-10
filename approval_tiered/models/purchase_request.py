from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    approval_stage = fields.Selection([
        ('draft', 'Draft'),
        ('one_approval', 'One Approval'),
        ('waiting_approval', 'Waiting Approval'),  # New stage added here
        ('two_approvals', 'Two Approvals'),
        ('approved', 'Approved')
    ], string="Approval Stage", default='draft')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('one_approval', 'One Approval'),
        ('waiting_approval', 'Waiting Second Approval'),
        ('approved', 'Approved')
    ], string="State", default='draft', tracking=True)

    approval_signature_1 = fields.Binary(string="First Approval Signature")
    approval_signature_2 = fields.Binary(string="Second Approval Signature")
    approver_id = fields.Many2one('res.users', string="Approver")
    second_approver_id = fields.Many2one('res.users', string="Second Approver")
    total_estimated_cost = fields.Monetary(
        string="Total Estimated Cost",
        compute="_compute_total_estimated_cost",
        store=True
    )
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)

    @api.depends('line_ids.estimated_cost')
    def _compute_total_estimated_cost(self):
        for request in self:
            request.total_estimated_cost = sum(line.estimated_cost for line in request.line_ids)

    def button_request_approval(self):
        approval_amount_1 = float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_1', default=5000000))
        approval_amount_2 = float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_2', default=10000000))

        # Approval logic (first approval logic by staff)
        if self.total_estimated_cost <= approval_amount_1:
            self.approval_stage = 'one_approval'
            self.state = 'one_approval'
            self.approver_id = self.env.user  # Automatically set approver to current user
        elif self.total_estimated_cost > approval_amount_1:
            self.approval_stage = 'waiting_approval'  # Move to 'waiting approval' stage
            self.approver_id = self.env.user  # Set first approver
            self.state = 'waiting_approval'
        
        # Debugging prints to check values
        print(f"First approval amount: {approval_amount_1}")
        print(f"Second approval amount: {approval_amount_2}")
        print(f"Total estimated cost: {self.total_estimated_cost}")
       
        # Trigger the signature capture wizard after setting the approval stage
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approve with Signature'),
            'res_model': 'purchase.request.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_request_id': self.id,
                'default_stage': self.approval_stage
            },
        }

    # Define the button_approve method to finalize the approval
    def button_approve(self):
    # First approval by staff
        if self.approval_stage == 'one_approval':
            print("=== First approval process started ===")
            
            # Ensure that the user provides a signature
            if not self.env.user.signature:
                raise UserError("You must sign before approving.")

            # Capture the first approval signature and approver
            self.approval_signature_1 = self.env.user.signature
            self.approver_id = self.env.user

            if self.total_estimated_cost > 5000000:
                # Move to second approval stage
                self.approval_stage = 'waiting_approval'
                self.state = 'waiting_approval'  # Waiting for second approval
                print(f"First approval by {self.env.user.name}, waiting for second approval")
                
                # Trigger second signature wizard for the second approver (manager)
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Second Approval with Signature'),
                    'res_model': 'purchase.request.signature.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_purchase_request_id': self.id,
                        'default_stage': 'two_approvals'
                    },
                }
            else:
                # If the cost is below the second threshold, approve immediately
                self.approval_stage = 'approved'
                self.state = 'approved'
                print(f"Purchase request approved by {self.env.user.name}, no second approval needed")

        # Second approval by manager
        elif self.approval_stage == 'waiting_approval':
            print("=== Second approval process started ===")
            
            # Check if the user is a manager
            if not self.env.user.has_group('purchase_request.group_purchase_request_manager'):
                raise AccessError("Only managers can approve this request.")

            
            # Capture the second approval signature and approver
            self.approval_signature_2 = self.env.user.signature
            self.second_approver_id = self.env.user
            self.approval_stage = 'approved'
            self.state = 'approved'
            print(f"Purchase request fully approved by {self.env.user.signature}")
            return {
                'type': 'ir.actions.act_window',
                'name': _('Second Approval with Signature'),
                'res_model': 'purchase.request.signature.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_request_id': self.id,
                    'default_stage': 'two_approvals'
            },
        }

        else:
            raise UserError("Approval process is not in the correct stage.")