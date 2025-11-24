# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class HospitalPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        """Añade contadores del hospital al portal"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        HospitalPatient = request.env['hospital.patient']
        HospitalAppointment = request.env['hospital.appointment']
        HospitalPrescription = request.env['hospital.prescription']
        
        patient = HospitalPatient.search([('partner_id', '=', partner.id)], limit=1)
        
        if patient and 'appointment_count' in counters:
            values['appointment_count'] = HospitalAppointment.search_count([
                ('patient_id', '=', patient.id)
            ])
        
        if patient and 'prescription_count' in counters:
            values['prescription_count'] = HospitalPrescription.search_count([
                ('patient_id', '=', patient.id)
            ])
        
        return values
    
    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_appointments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """Lista de citas del paciente"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        HospitalPatient = request.env['hospital.patient']
        HospitalAppointment = request.env['hospital.appointment']
        
        patient = HospitalPatient.search([('partner_id', '=', partner.id)], limit=1)
        
        if not patient:
            return request.render("citas_hospital.portal_no_patient", values)
        
        domain = [('patient_id', '=', patient.id)]
        
        searchbar_sortings = {
            'date': {'label': _('Fecha'), 'order': 'appointment_date desc'},
            'name': {'label': _('Número'), 'order': 'name'},
            'doctor': {'label': _('Doctor'), 'order': 'doctor_id'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # Conteo
        appointment_count = HospitalAppointment.search_count(domain)
        
        # Paginación
        pager = portal_pager(
            url="/my/appointments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=appointment_count,
            page=page,
            step=self._items_per_page
        )
        
        # Buscar citas
        appointments = HospitalAppointment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'appointments': appointments,
            'page_name': 'appointment',
            'pager': pager,
            'default_url': '/my/appointments',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        return request.render("citas_hospital.portal_my_appointments", values)
    
    @http.route(['/my/appointments/<int:appointment_id>'], type='http', auth="user", website=True)
    def portal_appointment_detail(self, appointment_id, access_token=None, **kw):
        """Detalle de una cita"""
        try:
            appointment_sudo = self._document_check_access('hospital.appointment', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'appointment': appointment_sudo,
            'page_name': 'appointment',
        }
        
        return request.render("citas_hospital.portal_appointment_detail", values)
    
    @http.route(['/my/prescriptions', '/my/prescriptions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_prescriptions(self, page=1, sortby=None, **kw):
        """Lista de recetas del paciente"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        HospitalPatient = request.env['hospital.patient']
        HospitalPrescription = request.env['hospital.prescription']
        
        patient = HospitalPatient.search([('partner_id', '=', partner.id)], limit=1)
        
        if not patient:
            return request.render("citas_hospital.portal_no_patient", values)
        
        domain = [('patient_id', '=', patient.id)]
        
        searchbar_sortings = {
            'date': {'label': _('Fecha'), 'order': 'prescription_date desc'},
            'name': {'label': _('Número'), 'order': 'name'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # Conteo
        prescription_count = HospitalPrescription.search_count(domain)
        
        # Paginación
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={'sortby': sortby},
            total=prescription_count,
            page=page,
            step=self._items_per_page
        )
        
        # Buscar recetas
        prescriptions = HospitalPrescription.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'prescriptions': prescriptions,
            'page_name': 'prescription',
            'pager': pager,
            'default_url': '/my/prescriptions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        return request.render("citas_hospital.portal_my_prescriptions", values)
    
    @http.route(['/my/prescriptions/<int:prescription_id>'], type='http', auth="user", website=True)
    def portal_prescription_detail(self, prescription_id, access_token=None, **kw):
        """Detalle de una receta"""
        try:
            prescription_sudo = self._document_check_access('hospital.prescription', prescription_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'prescription': prescription_sudo,
            'page_name': 'prescription',
        }
        
        return request.render("citas_hospital.portal_prescription_detail", values)
    
    @http.route(['/my/appointments/<int:appointment_id>/cancel'], type='http', auth="user", website=True, methods=['POST'])
    def portal_appointment_cancel(self, appointment_id, cancellation_reason, **kw):
        """Cancelar una cita desde el portal"""
        try:
            appointment_sudo = self._document_check_access('hospital.appointment', appointment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if appointment_sudo.state in ['draft', 'confirmed']:
            appointment_sudo.write({
                'state': 'cancelled',
                'cancellation_reason': cancellation_reason
            })
            if appointment_sudo.calendar_event_id:
                appointment_sudo.calendar_event_id.unlink()
        
        return request.redirect('/my/appointments')
