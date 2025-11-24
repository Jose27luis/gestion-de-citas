# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HospitalDoctor(models.Model):
    """Modelo para gestionar doctores del hospital"""
    _name = 'hospital.doctor'
    _description = 'Doctor del Hospital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Campos básicos
    name = fields.Char(
        string='Nombre Completo',
        required=True,
        tracking=True,
        index=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado Relacionado',
        ondelete='restrict',
        help='Empleado de Recursos Humanos vinculado'
    )
    license_number = fields.Char(
        string='Número de Licencia Médica',
        required=True,
        tracking=True,
        index=True,
        help='Número de colegiatura o licencia profesional'
    )
    
    # Especialidades
    specialty_ids = fields.Many2many(
        'hospital.specialty',
        'doctor_specialty_rel',
        'doctor_id',
        'specialty_id',
        string='Especialidades',
        tracking=True
    )
    
    # Contacto
    phone = fields.Char(string='Teléfono', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    
    # Relaciones
    schedule_ids = fields.One2many(
        'hospital.schedule',
        'doctor_id',
        string='Horarios'
    )
    appointment_ids = fields.One2many(
        'hospital.appointment',
        'doctor_id',
        string='Citas'
    )
    prescription_ids = fields.One2many(
        'hospital.prescription',
        'doctor_id',
        string='Recetas'
    )
    
    # Información adicional
    consultation_room = fields.Char(
        string='Consultorio',
        tracking=True
    )
    biography = fields.Html(
        string='Biografía',
        help='Información profesional del doctor'
    )
    years_experience = fields.Integer(
        string='Años de Experiencia',
        tracking=True
    )
    
    # Contadores para smart buttons
    appointment_today_count = fields.Integer(
        string='Citas Hoy',
        compute='_compute_appointment_today_count'
    )
    appointment_pending_count = fields.Integer(
        string='Citas Pendientes',
        compute='_compute_appointment_pending_count'
    )
    prescription_count = fields.Integer(
        string='Total Recetas',
        compute='_compute_prescription_count'
    )
    
    # Otros
    active = fields.Boolean(string='Activo', default=True)
    image_1920 = fields.Image(string='Foto', max_width=1920, max_height=1920)
    color = fields.Integer(string='Color')
    
    # Constraints SQL
    _sql_constraints = [
        ('license_unique', 'UNIQUE(license_number)',
         'El número de licencia médica debe ser único!')
    ]
    
    @api.depends('appointment_ids')
    def _compute_appointment_today_count(self):
        """Cuenta las citas del doctor para hoy"""
        today = datetime.now().date()
        for record in self:
            record.appointment_today_count = self.env['hospital.appointment'].search_count([
                ('doctor_id', '=', record.id),
                ('appointment_date', '>=', today),
                ('appointment_date', '<', today + timedelta(days=1)),
                ('state', 'in', ['confirmed', 'in_progress'])
            ])
    
    @api.depends('appointment_ids')
    def _compute_appointment_pending_count(self):
        """Cuenta las citas pendientes de confirmación"""
        for record in self:
            record.appointment_pending_count = self.env['hospital.appointment'].search_count([
                ('doctor_id', '=', record.id),
                ('state', '=', 'draft')
            ])
    
    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        """Cuenta el total de recetas emitidas"""
        for record in self:
            record.prescription_count = len(record.prescription_ids)
    
    def action_view_appointments_today(self):
        """Acción para ver las citas de hoy"""
        self.ensure_one()
        today = datetime.now().date()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Citas de Hoy - %s') % self.name,
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [
                ('doctor_id', '=', self.id),
                ('appointment_date', '>=', today),
                ('appointment_date', '<', today + timedelta(days=1))
            ],
            'context': {'default_doctor_id': self.id},
        }
    
    def action_view_appointments_pending(self):
        """Acción para ver las citas pendientes"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Citas Pendientes - %s') % self.name,
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form',
            'domain': [
                ('doctor_id', '=', self.id),
                ('state', '=', 'draft')
            ],
            'context': {'default_doctor_id': self.id},
        }
    
    def action_view_prescriptions(self):
        """Acción para ver las recetas emitidas"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Recetas de %s') % self.name,
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
        }
    
    @api.constrains('years_experience')
    def _check_years_experience(self):
        """Valida los años de experiencia"""
        for record in self:
            if record.years_experience < 0:
                raise ValidationError(
                    _('Los años de experiencia no pueden ser negativos.')
                )
            if record.years_experience > 70:
                raise ValidationError(
                    _('Los años de experiencia no pueden exceder 70 años.')
                )
    
    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        for record in self:
            specialties = ', '.join(record.specialty_ids.mapped('code'))
            if specialties:
                name = f"Dr(a). {record.name} - {specialties}"
            else:
                name = f"Dr(a). {record.name}"
            result.append((record.id, name))
        return result
