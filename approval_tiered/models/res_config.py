from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_amount_1 = fields.Monetary(
        string='Single Approval Threshold',
        help='The maximum amount for a single approval',
        default=5000000
    )
    approval_amount_2 = fields.Monetary(
        string='Double Approval Threshold',
        help='The maximum amount for double approvals',
        default=10000000
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'approval_amount_1': float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_1', default=5000000)),
            'approval_amount_2': float(self.env['ir.config_parameter'].sudo().get_param('tiered_approval_purchase.approval_amount_2', default=10000000)),
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('tiered_approval_purchase.approval_amount_1', self.approval_amount_1)
        self.env['ir.config_parameter'].sudo().set_param('tiered_approval_purchase.approval_amount_2', self.approval_amount_2)
