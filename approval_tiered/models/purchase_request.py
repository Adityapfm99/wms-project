from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    approval_stage = fields.Selection([
        ('draft', 'Draft'),
        ('one_approval', 'One Approval'),
        ('waiting_approval', 'Waiting Approval'),  # New stage added here
        ('two_approvals', 'Two Approvals'),
        ('approved', 'Approved'),
        ('done', 'Done')
    ], string="Approval Stage", default='draft')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('one_approval', 'One Approval'),
        ('waiting_approval', 'Waiting Second Approval'),
        ('approved', 'Approved'),
        ('done', 'Done')
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
    # Check if the user is a Purchase Manager
        if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
            # Manager approval logic here (existing code)
            approval_amount_1 = float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_1', default=5000000))
            approval_amount_2 = float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_2', default=10000000))

            # Approval logic by Purchase Manager
            if self.total_estimated_cost <= approval_amount_1:
                self.approval_stage = 'one_approval'
                self.state = 'one_approval'
                self.approver_id = self.env.user  # Automatically set approver to current user
            elif self.total_estimated_cost > approval_amount_1:
                self.approval_stage = 'waiting_approval'  # Move to 'waiting approval' stage
                self.approver_id = self.env.user  # Set first approver
                self.state = 'waiting_approval'

            # Trigger signature wizard for approval (if applicable)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Approve with Signature First Approval'),
                'res_model': 'purchase.request.first.approval.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_request_id': self.id,
                    'default_stage': 'waiting_approval'
                },
            }

        # If the user is not a manager (Purchase User), show the creation signature wizard
        elif self.env.user.has_group('purchase_request.group_purchase_request_user'):
            # Show creation signature wizard for purchase user and move to "one_approval" after signing
            self.state = 'one_approval'  # Change the state to one_approval
            self.approval_stage = 'one_approval'  # Change the approval stage

            return {
                'type': 'ir.actions.act_window',
                'name': 'Sign Purchase Request Creation',
                'res_model': 'purchase.request.creation.signature.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_request_id': self.id,  # Passing the request ID to the wizard
                },
            }
        
        # If neither, raise an access error
        else:
            raise AccessError("You don't have the required access rights.")

    # Define the button_approve method to finalize the approval
    def button_approve(self):
    # Second approval by manager (only triggered if approval_stage == 'waiting_approval')
        if self.approval_stage == 'waiting_approval':
            print("=== Second approval process started ===")
            
            # Check if the user is a manager
            if not self.env.user.has_group('purchase_request.group_purchase_request_manager'):
                raise AccessError("Only managers can approve this request.")

            # Trigger the signature wizard for the second approver (manager)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Second Approval with Signature Second'),
                'res_model': 'purchase.request.second.approval.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_purchase_request_id': self.id,
                    'default_stage': 'approve',  # Waiting for second approval
                },
            
            }