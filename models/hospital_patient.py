# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class HospitalPatient(models.Model):
    """Modelo para gestionar pacientes del hospital"""
    _name = 'hospital.patient'
    _description = 'Paciente del Hospital'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name'
    
    # Campos básicos
    name = fields.Char(
        string='Nombre Completo',
        required=True,
        tracking=True,
        index=True
    )
    identification_id = fields.Char(
        string='DNI/Cédula',
        required=True,
        tracking=True,
        index=True,
        help='Documento de identidad único del paciente'
    )
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        tracking=True
    )
    age = fields.Integer(
        string='Edad',
        compute='_compute_age',
        store=True,
        help='Edad calculada automáticamente'
    )
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género', tracking=True)
    
    blood_type = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Tipo de Sangre', tracking=True)
    
    # Contacto
    phone = fields.Char(string='Teléfono', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Text(string='Dirección')
    
    # Relación con partner
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto Relacionado',
        ondelete='restrict',
        help='Contacto de Odoo vinculado al paciente'
    )
    
    # Información médica
    allergies = fields.Text(string='Alergias', tracking=True)
    medical_history = fields.Html(
        string='Historial Médico',
        tracking=True
    )
    
    # Contacto de emergencia
    emergency_contact = fields.Char(
        string='Contacto de Emergencia',
        tracking=True
    )
    emergency_phone = fields.Char(
        string='Teléfono de Emergencia',
        tracking=True
    )
    
    # Relaciones
    appointment_ids = fields.One2many(
        'hospital.appointment',
        'patient_id',
        string='Citas'
    )
    prescription_ids = fields.One2many(
        'hospital.prescription',
        'patient_id',
        string='Recetas'
    )
    
    # Contadores para smart buttons
    appointment_count = fields.Integer(
        string='Total Citas',
        compute='_compute_appointment_count'
    )
    prescription_count = fields.Integer(
        string='Total Recetas',
        compute='_compute_prescription_count'
    )
    
    # Otros
    active = fields.Boolean(string='Activo', default=True)
    image_1920 = fields.Image(string='Foto', max_width=1920, max_height=1920)
    
    # Constraints SQL
    _sql_constraints = [
        ('identification_unique', 'UNIQUE(identification_id)',
         'El número de identificación debe ser único!')
    ]
    
    @api.depends('birth_date')
    def _compute_age(self):
        """Calcula la edad del paciente basado en su fecha de nacimiento"""
        today = date.today()
        for record in self:
            if record.birth_date:
                record.age = relativedelta(today, record.birth_date).years
            else:
                record.age = 0
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        """Cuenta el total de citas del paciente"""
        for record in self:
            record.appointment_count = len(record.appointment_ids)
    
    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        """Cuenta el total de recetas del paciente"""
        for record in self:
            record.prescription_count = len(record.prescription_ids)
    
    @api.model
    def create(self, vals):
        """Crea automáticamente un partner si no existe"""
        result = super(HospitalPatient, self).create(vals)
        
        if not result.partner_id and result.email:
            partner = self.env['res.partner'].create({
                'name': result.name,
                'email': result.email,
                'phone': result.phone,
                'street': result.address,
                'type': 'contact',
            })
            result.partner_id = partner.id
        
        return result
    
    def action_view_appointments(self):
        """Acción para abrir las citas del paciente"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Citas de %s') % self.name,
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    def action_view_prescriptions(self):
        """Acción para abrir las recetas del paciente"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Recetas de %s') % self.name,
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    @api.constrains('birth_date')
    def _check_birth_date(self):
        """Valida que la fecha de nacimiento no sea futura"""
        for record in self:
            if record.birth_date and record.birth_date > date.today():
                raise ValidationError(_('La fecha de nacimiento no puede ser futura.'))
    
    @api.constrains('email')
    def _check_email(self):
        """Valida formato de email"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(_('El formato del email no es válido.'))
    
    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        for record in self:
            name = f"{record.name} ({record.identification_id})"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """Búsqueda inteligente por nombre, DNI o teléfono"""
        if domain is None:
            domain = []
        
        if name:
            domain = ['|', '|',
                      ('name', operator, name),
                      ('identification_id', operator, name),
                      ('phone', operator, name)]
        
        return self._search(domain, limit=limit, order=order)
