# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AppointmentCancelWizard(models.TransientModel):
    """Wizard para cancelar citas con motivo"""
    _name = 'appointment.cancel.wizard'
    _description = 'Wizard para Cancelar Cita'
    
    appointment_id = fields.Many2one(
        'hospital.appointment',
        string='Cita',
        required=True,
        ondelete='cascade'
    )
    cancellation_reason = fields.Text(
        string='Motivo de Cancelación',
        required=True,
        help='Indique el motivo de la cancelación de la cita'
    )
    
    def action_confirm_cancel(self):
        """Confirma la cancelación de la cita"""
        self.ensure_one()
        
        if self.appointment_id.state == 'cancelled':
            raise UserError(_('Esta cita ya está cancelada.'))
        
        if self.appointment_id.state == 'done':
            raise UserError(_('No se puede cancelar una cita ya realizada.'))
        
        # Cancelar cita
        self.appointment_id.write({
            'state': 'cancelled',
            'cancellation_reason': self.cancellation_reason
        })
        
        # Eliminar evento de calendario si existe
        if self.appointment_id.calendar_event_id:
            self.appointment_id.calendar_event_id.unlink()
        
        return {'type': 'ir.actions.act_window_close'}
