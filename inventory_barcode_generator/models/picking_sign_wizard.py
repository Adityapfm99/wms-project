import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class PickingSignWizard(models.TransientModel):
    _name = 'picking.sign.wizard'
    _description = 'Picking Sign Wizard'

    picking_id = fields.Many2one('stock.picking', string='Picking', required=True)
    signature = fields.Binary(string='Signature', required=True)

    def action_confirm_signature(self):
        if not self.signature:
            raise KeyError("Please provide a signature before confirming...")

        current_state = self.picking_id.state
        _logger.info(f"Current state of the picking: {current_state}")

        self.picking_id.signature_image = self.signature
        self.picking_id.button_validate()
        new_state = self.picking_id.state
        _logger.info(f"New state of the picking after validation: {new_state}")
        _logger.info(f"Stock picking {self.picking_id.name} validated")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Picking validated successfully.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            },
        }