# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HospitalPrescriptionLine(models.Model):
    """Modelo para líneas de recetas médicas"""
    _name = 'hospital.prescription.line'
    _description = 'Línea de Receta Médica'
    _order = 'prescription_id, sequence, id'
    
    sequence = fields.Integer(string='Secuencia', default=10)
    
    prescription_id = fields.Many2one(
        'hospital.prescription',
        string='Receta',
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Medicamento',
        required=True,
        domain="[('is_medication', '=', True)]",
        ondelete='restrict'
    )
    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits='Product Unit of Measure'
    )
    dosage = fields.Char(
        string='Dosis',
        help='Ejemplo: 500mg, 10ml, 1 tableta'
    )
    frequency = fields.Char(
        string='Frecuencia',
        help='Ejemplo: Cada 8 horas, 3 veces al día'
    )
    duration = fields.Char(
        string='Duración',
        help='Ejemplo: 7 días, 2 semanas'
    )
    instructions = fields.Text(
        string='Instrucciones',
        help='Instrucciones adicionales para tomar el medicamento'
    )
    available_qty = fields.Float(
        string='Stock Disponible',
        related='product_id.qty_available',
        readonly=True
    )
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """Valida la cantidad"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(
                    _('La cantidad debe ser mayor a 0.')
                )
    
    def _check_stock(self):
        """Verifica el stock disponible"""
        for record in self:
            if record.available_qty < record.quantity:
                return {
                    'warning': {
                        'title': _('Stock Insuficiente'),
                        'message': _(
                            'El medicamento %s tiene stock insuficiente.\n'
                            'Stock disponible: %.2f\n'
                            'Cantidad solicitada: %.2f'
                        ) % (record.product_id.name, record.available_qty, record.quantity)
                    }
                }
        return True
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Verifica stock al cambiar producto"""
        if self.product_id:
            self._check_stock()
    
    @api.onchange('quantity')
    def _onchange_quantity(self):
        """Verifica stock al cambiar cantidad"""
        if self.product_id and self.quantity:
            self._check_stock()
