# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    """Extensión del modelo de productos para medicamentos"""
    _inherit = 'product.product'
    
    is_medication = fields.Boolean(
        string='Es Medicamento',
        default=False,
        help='Marca este producto como medicamento'
    )
    active_ingredient = fields.Char(
        string='Principio Activo',
        help='Ingrediente activo del medicamento'
    )
    concentration = fields.Char(
        string='Concentración',
        help='Ejemplo: 500mg, 10mg/ml'
    )
    pharmaceutical_form = fields.Selection([
        ('tablet', 'Tableta'),
        ('capsule', 'Cápsula'),
        ('syrup', 'Jarabe'),
        ('injection', 'Inyectable'),
        ('cream', 'Crema'),
        ('ointment', 'Ungüento'),
        ('drops', 'Gotas'),
        ('inhaler', 'Inhalador'),
        ('suppository', 'Supositorio'),
        ('patch', 'Parche'),
        ('other', 'Otro'),
    ], string='Forma Farmacéutica')
    
    requires_prescription = fields.Boolean(
        string='Requiere Receta',
        default=True,
        help='Indica si el medicamento requiere receta médica'
    )
    contraindications = fields.Text(
        string='Contraindicaciones',
        help='Contraindicaciones y advertencias del medicamento'
    )
    
    @api.onchange('is_medication')
    def _onchange_is_medication(self):
        """Establece valores por defecto al marcar como medicamento"""
        if self.is_medication:
            self.type = 'product'
            self.detailed_type = 'product'
