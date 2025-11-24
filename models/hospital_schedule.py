# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalSchedule(models.Model):
    """Modelo para gestionar horarios de los doctores"""
    _name = 'hospital.schedule'
    _description = 'Horario del Doctor'
    _order = 'day_of_week, hour_from'
    
    doctor_id = fields.Many2one(
        'hospital.doctor',
        string='Doctor',
        required=True,
        ondelete='cascade',
        index=True
    )
    day_of_week = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo'),
    ], string='Día de la Semana', required=True, index=True)
    
    hour_from = fields.Float(
        string='Hora Desde',
        required=True,
        help='Hora de inicio en formato 24h (8.0 = 8:00 AM, 14.5 = 2:30 PM)'
    )
    hour_to = fields.Float(
        string='Hora Hasta',
        required=True,
        help='Hora de fin en formato 24h'
    )
    slot_duration = fields.Float(
        string='Duración de Slot (minutos)',
        default=30.0,
        help='Duración de cada slot de cita en minutos'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    @api.constrains('hour_from', 'hour_to')
    def _check_hours(self):
        """Valida que las horas sean válidas"""
        for record in self:
            if record.hour_to <= record.hour_from:
                raise ValidationError(
                    _('La hora de fin debe ser posterior a la hora de inicio.')
                )
            if record.hour_from < 0 or record.hour_from >= 24:
                raise ValidationError(
                    _('La hora de inicio debe estar entre 0 y 24.')
                )
            if record.hour_to < 0 or record.hour_to > 24:
                raise ValidationError(
                    _('La hora de fin debe estar entre 0 y 24.')
                )
    
    @api.constrains('slot_duration')
    def _check_slot_duration(self):
        """Valida la duración del slot"""
        for record in self:
            if record.slot_duration <= 0:
                raise ValidationError(
                    _('La duración del slot debe ser mayor a 0.')
                )
            if record.slot_duration > 480:  # 8 horas en minutos
                raise ValidationError(
                    _('La duración del slot no puede exceder 8 horas.')
                )
    
    @api.constrains('doctor_id', 'day_of_week', 'hour_from', 'hour_to')
    def _check_schedule_overlap(self):
        """Valida que no haya solapamiento de horarios para el mismo doctor"""
        for record in self:
            overlapping = self.search([
                ('doctor_id', '=', record.doctor_id.id),
                ('day_of_week', '=', record.day_of_week),
                ('id', '!=', record.id),
                ('active', '=', True),
                '|',
                '&', ('hour_from', '<=', record.hour_from), ('hour_to', '>', record.hour_from),
                '&', ('hour_from', '<', record.hour_to), ('hour_to', '>=', record.hour_to),
            ])
            if overlapping:
                raise ValidationError(
                    _('Este horario se solapa con otro horario existente del mismo doctor.')
                )
    
    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        days = dict(self._fields['day_of_week'].selection)
        for record in self:
            hour_from = '{:02.0f}:{:02.0f}'.format(*divmod(record.hour_from * 60, 60))
            hour_to = '{:02.0f}:{:02.0f}'.format(*divmod(record.hour_to * 60, 60))
            name = f"{days.get(record.day_of_week)} {hour_from} - {hour_to}"
            result.append((record.id, name))
        return result
