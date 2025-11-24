# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class HospitalAppointment(models.Model):
    """Modelo para gestionar citas médicas"""
    _name = 'hospital.appointment'
    _description = 'Cita Médica'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc'
    
    name = fields.Char(
        string='Número de Cita',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('Nuevo')
    )
    patient_id = fields.Many2one(
        'hospital.patient',
        string='Paciente',
        required=True,
        tracking=True,
        ondelete='restrict',
        index=True
    )
    doctor_id = fields.Many2one(
        'hospital.doctor',
        string='Doctor',
        required=True,
        tracking=True,
        ondelete='restrict',
        index=True
    )
    specialty_id = fields.Many2one(
        'hospital.specialty',
        string='Especialidad',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    appointment_date = fields.Datetime(
        string='Fecha y Hora',
        required=True,
        tracking=True,
        index=True
    )
    duration = fields.Float(
        string='Duración (horas)',
        default=0.5,
        help='Duración de la cita en horas'
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('done', 'Realizada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    reason = fields.Text(
        string='Motivo de Consulta',
        tracking=True
    )
    notes = fields.Html(
        string='Notas',
        tracking=True
    )
    prescription_id = fields.Many2one(
        'hospital.prescription',
        string='Receta',
        ondelete='restrict',
        readonly=True
    )
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Evento de Calendario',
        ondelete='set null',
        readonly=True
    )
    color = fields.Integer(
        string='Color',
        related='specialty_id.color',
        store=True
    )
    confirmation_date = fields.Datetime(
        string='Fecha de Confirmación',
        readonly=True,
        tracking=True
    )
    cancellation_reason = fields.Text(
        string='Motivo de Cancelación',
        tracking=True
    )
    
    # Constraint SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'El número de cita debe ser único!')
    ]
    
    @api.model
    def create(self, vals):
        """Genera secuencia automática al crear"""
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('Nuevo')
        
        result = super(HospitalAppointment, self).create(vals)
        
        # Crear evento en calendario
        if result.state == 'confirmed':
            result._create_calendar_event()
        
        return result
    
    def write(self, vals):
        """Override para manejar eventos de calendario"""
        result = super(HospitalAppointment, self).write(vals)
        
        # Actualizar evento de calendario si existe
        for record in self:
            if record.calendar_event_id and record.state == 'confirmed':
                record._update_calendar_event()
            elif record.state == 'cancelled' and record.calendar_event_id:
                record.calendar_event_id.unlink()
                record.calendar_event_id = False
        
        return result
    
    def action_confirm(self):
        """Confirma la cita"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Solo se pueden confirmar citas en estado borrador.'))
            
            # Verificar disponibilidad del doctor
            record._check_doctor_availability()
            
            record.write({
                'state': 'confirmed',
                'confirmation_date': datetime.now()
            })
            
            # Crear evento en calendario
            record._create_calendar_event()
            
            # Enviar notificación
            record._send_confirmation_email()
    
    def action_start(self):
        """Inicia la cita"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_('Solo se pueden iniciar citas confirmadas.'))
            
            record.state = 'in_progress'
    
    def action_done(self):
        """Marca la cita como realizada"""
        for record in self:
            if record.state not in ['confirmed', 'in_progress']:
                raise UserError(_('Solo se pueden finalizar citas confirmadas o en progreso.'))
            
            record.state = 'done'
    
    def action_cancel(self):
        """Cancela la cita - abre wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancelar Cita'),
            'res_model': 'appointment.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_appointment_id': self.id},
        }
    
    def action_create_prescription(self):
        """Crea una receta para esta cita"""
        self.ensure_one()
        
        if self.state != 'in_progress' and self.state != 'done':
            raise UserError(_('Solo se pueden crear recetas para citas en progreso o realizadas.'))
        
        prescription = self.env['hospital.prescription'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'appointment_id': self.id,
        })
        
        self.prescription_id = prescription.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Receta'),
            'res_model': 'hospital.prescription',
            'res_id': prescription.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _check_doctor_availability(self):
        """Verifica disponibilidad del doctor"""
        self.ensure_one()
        
        # Buscar citas que se solapen
        overlapping = self.env['hospital.appointment'].search([
            ('doctor_id', '=', self.doctor_id.id),
            ('id', '!=', self.id),
            ('state', 'in', ['confirmed', 'in_progress']),
            ('appointment_date', '<', self.appointment_date + timedelta(hours=self.duration)),
            ('appointment_date', '>', self.appointment_date - timedelta(hours=1)),
        ])
        
        if overlapping:
            raise ValidationError(
                _('El doctor ya tiene una cita programada en este horario.')
            )
    
    def _create_calendar_event(self):
        """Crea un evento en el calendario"""
        self.ensure_one()
        
        if self.calendar_event_id:
            return
        
        event = self.env['calendar.event'].create({
            'name': f"Cita: {self.patient_id.name} - {self.doctor_id.name}",
            'start': self.appointment_date,
            'stop': self.appointment_date + timedelta(hours=self.duration),
            'description': self.reason or '',
            'location': self.doctor_id.consultation_room or '',
            'partner_ids': [(6, 0, [self.doctor_id.employee_id.user_id.partner_id.id])] if self.doctor_id.employee_id and self.doctor_id.employee_id.user_id else [],
        })
        
        self.calendar_event_id = event.id
    
    def _update_calendar_event(self):
        """Actualiza el evento de calendario"""
        self.ensure_one()
        
        if not self.calendar_event_id:
            return
        
        self.calendar_event_id.write({
            'name': f"Cita: {self.patient_id.name} - {self.doctor_id.name}",
            'start': self.appointment_date,
            'stop': self.appointment_date + timedelta(hours=self.duration),
            'description': self.reason or '',
            'location': self.doctor_id.consultation_room or '',
        })
    
    def _send_confirmation_email(self):
        """Envía email de confirmación"""
        self.ensure_one()
        
        template = self.env.ref('citas_hospital.mail_template_appointment_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
    
    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        """Valida que la fecha sea futura"""
        for record in self:
            if record.appointment_date and record.appointment_date < datetime.now() and record.state == 'draft':
                raise ValidationError(
                    _('La fecha de la cita debe ser futura.')
                )
    
    @api.constrains('doctor_id', 'specialty_id')
    def _check_doctor_specialty(self):
        """Valida que el doctor tenga la especialidad"""
        for record in self:
            if record.specialty_id not in record.doctor_id.specialty_ids:
                raise ValidationError(
                    _('El doctor seleccionado no tiene la especialidad indicada.')
                )
    
    @api.constrains('duration')
    def _check_duration(self):
        """Valida la duración"""
        for record in self:
            if record.duration <= 0:
                raise ValidationError(
                    _('La duración debe ser mayor a 0.')
                )
            if record.duration > 8:
                raise ValidationError(
                    _('La duración no puede exceder 8 horas.')
                )
    
    @api.model
    def _cron_send_reminders_24h(self):
        """Cron: Envía recordatorios 24 horas antes"""
        tomorrow = datetime.now() + timedelta(days=1)
        appointments = self.search([
            ('state', '=', 'confirmed'),
            ('appointment_date', '>=', tomorrow),
            ('appointment_date', '<=', tomorrow + timedelta(hours=1)),
        ])
        
        template = self.env.ref('citas_hospital.mail_template_appointment_reminder_24h', raise_if_not_found=False)
        for appointment in appointments:
            if template:
                template.send_mail(appointment.id, force_send=True)
    
    @api.model
    def _cron_send_reminders_2h(self):
        """Cron: Envía recordatorios 2 horas antes"""
        in_2h = datetime.now() + timedelta(hours=2)
        appointments = self.search([
            ('state', '=', 'confirmed'),
            ('appointment_date', '>=', in_2h),
            ('appointment_date', '<=', in_2h + timedelta(minutes=30)),
        ])
        
        template = self.env.ref('citas_hospital.mail_template_appointment_reminder_2h', raise_if_not_found=False)
        for appointment in appointments:
            if template:
                template.send_mail(appointment.id, force_send=True)
            
            # Crear actividad para el doctor
            if appointment.doctor_id.employee_id and appointment.doctor_id.employee_id.user_id:
                appointment.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=appointment.doctor_id.employee_id.user_id.id,
                    note=f'Cita en 30 minutos con {appointment.patient_id.name}',
                    date_deadline=appointment.appointment_date.date(),
                )
    
    @api.model
    def _cron_auto_cancel_unconfirmed(self):
        """Cron: Cancela citas no confirmadas 1 hora antes"""
        in_1h = datetime.now() + timedelta(hours=1)
        appointments = self.search([
            ('state', '=', 'draft'),
            ('appointment_date', '<=', in_1h),
        ])
        
        for appointment in appointments:
            appointment.write({
                'state': 'cancelled',
                'cancellation_reason': 'Cancelada automáticamente por falta de confirmación.'
            })
