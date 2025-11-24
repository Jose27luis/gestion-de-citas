# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class HospitalPrescription(models.Model):
    """Modelo para gestionar recetas médicas"""
    _name = 'hospital.prescription'
    _description = 'Receta Médica'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'prescription_date desc'
    
    name = fields.Char(
        string='Número de Receta',
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
    appointment_id = fields.Many2one(
        'hospital.appointment',
        string='Cita Relacionada',
        ondelete='restrict'
    )
    prescription_date = fields.Date(
        string='Fecha de Emisión',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        index=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('issued', 'Emitida'),
        ('dispensed', 'Dispensada'),
        ('expired', 'Expirada'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    diagnosis = fields.Text(
        string='Diagnóstico',
        tracking=True
    )
    general_instructions = fields.Html(
        string='Instrucciones Generales',
        tracking=True
    )
    line_ids = fields.One2many(
        'hospital.prescription.line',
        'prescription_id',
        string='Líneas de Medicamentos'
    )
    validity_days = fields.Integer(
        string='Días de Validez',
        default=30,
        tracking=True,
        help='Días de validez de la receta desde su emisión'
    )
    expiry_date = fields.Date(
        string='Fecha de Expiración',
        compute='_compute_expiry_date',
        store=True
    )
    notes = fields.Text(
        string='Notas Adicionales',
        tracking=True
    )
    
    # Constraint SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'El número de receta debe ser único!')
    ]
    
    @api.depends('prescription_date', 'validity_days')
    def _compute_expiry_date(self):
        """Calcula la fecha de expiración"""
        for record in self:
            if record.prescription_date and record.validity_days:
                record.expiry_date = record.prescription_date + timedelta(days=record.validity_days)
            else:
                record.expiry_date = False
    
    @api.model
    def create(self, vals):
        """Genera secuencia automática al crear"""
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.prescription') or _('Nuevo')
        
        return super(HospitalPrescription, self).create(vals)
    
    def action_issue(self):
        """Emite la receta"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Solo se pueden emitir recetas en estado borrador.'))
            
            if not record.line_ids:
                raise UserError(_('Debe agregar al menos un medicamento a la receta.'))
            
            # Verificar stock de todos los medicamentos
            for line in record.line_ids:
                line._check_stock()
            
            record.state = 'issued'
            
            # Enviar notificación
            record._send_issued_email()
    
    def action_dispense(self):
        """Marca la receta como dispensada"""
        for record in self:
            if record.state != 'issued':
                raise UserError(_('Solo se pueden dispensar recetas emitidas.'))
            
            # Verificar que no esté expirada
            record._check_expiry()
            
            record.state = 'dispensed'
    
    def _check_expiry(self):
        """Verifica si la receta está expirada"""
        self.ensure_one()
        
        if self.expiry_date and self.expiry_date < date.today():
            raise UserError(
                _('Esta receta ha expirado el %s.') % self.expiry_date.strftime('%d/%m/%Y')
            )
    
    def _send_issued_email(self):
        """Envía email al emitir la receta"""
        self.ensure_one()
        
        template = self.env.ref('citas_hospital.mail_template_prescription_issued', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
    
    @api.model
    def _cron_check_expiry(self):
        """Cron: Marca recetas expiradas"""
        today = date.today()
        expired = self.search([
            ('state', 'in', ['issued']),
            ('expiry_date', '<', today),
        ])
        
        for prescription in expired:
            prescription.state = 'expired'
    
    @api.constrains('validity_days')
    def _check_validity_days(self):
        """Valida los días de validez"""
        for record in self:
            if record.validity_days <= 0:
                raise ValidationError(
                    _('Los días de validez deben ser mayores a 0.')
                )
            if record.validity_days > 365:
                raise ValidationError(
                    _('Los días de validez no pueden exceder 365 días.')
                )
    
    def _compute_access_url(self):
        """Computa la URL para el portal"""
        super(HospitalPrescription, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/prescriptions/%s' % record.id
    
    def action_print_prescription(self):
        """Imprime la receta"""
        self.ensure_one()
        return self.env.ref('citas_hospital.action_report_prescription').report_action(self)
