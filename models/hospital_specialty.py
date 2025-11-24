# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalSpecialty(models.Model):
    """Modelo para gestionar especialidades médicas"""
    _name = 'hospital.specialty'
    _description = 'Especialidad Médica'
    _order = 'name'
    
    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
        index=True
    )
    code = fields.Char(
        string='Código',
        required=True,
        index=True,
        help='Código único de la especialidad'
    )
    description = fields.Text(
        string='Descripción',
        translate=True
    )
    doctor_ids = fields.Many2many(
        'hospital.doctor',
        'doctor_specialty_rel',
        'specialty_id',
        'doctor_id',
        string='Doctores'
    )
    doctor_count = fields.Integer(
        string='Cantidad de Doctores',
        compute='_compute_doctor_count'
    )
    appointment_duration = fields.Float(
        string='Duración de Cita (horas)',
        default=0.5,
        help='Duración predeterminada de citas en horas (0.5 = 30 minutos)'
    )
    color = fields.Integer(
        string='Color',
        help='Color para identificar visualmente la especialidad'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    # Constraints SQL
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)',
         'El código de la especialidad debe ser único!')
    ]
    
    @api.depends('doctor_ids')
    def _compute_doctor_count(self):
        """Cuenta la cantidad de doctores en esta especialidad"""
        for record in self:
            record.doctor_count = len(record.doctor_ids)
    
    @api.constrains('appointment_duration')
    def _check_appointment_duration(self):
        """Valida que la duración de cita sea positiva"""
        for record in self:
            if record.appointment_duration <= 0:
                raise ValidationError(
                    _('La duración de la cita debe ser mayor a 0.')
                )
            if record.appointment_duration > 8:
                raise ValidationError(
                    _('La duración de la cita no puede exceder 8 horas.')
                )
    
    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            result.append((record.id, name))
        return result
