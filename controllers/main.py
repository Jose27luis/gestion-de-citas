# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import json
from datetime import datetime, timedelta


class HospitalWebsite(http.Controller):
    
    @http.route(['/appointments/booking'], type='http', auth="public", website=True)
    def appointment_booking(self, **kw):
        """Página de reserva de citas online"""
        specialties = request.env['hospital.specialty'].sudo().search([('active', '=', True)])
        
        values = {
            'specialties': specialties,
            'page_name': 'appointment_booking',
        }
        
        return request.render("citas_hospital.website_appointment_booking", values)
    
    @http.route(['/appointments/booking/get_doctors'], type='json', auth="public", website=True)
    def get_doctors_by_specialty(self, specialty_id, **kw):
        """Obtiene doctores filtrados por especialidad (AJAX)"""
        doctors = request.env['hospital.doctor'].sudo().search([
            ('specialty_ids', 'in', [int(specialty_id)]),
            ('active', '=', True)
        ])
        
        return [{
            'id': doctor.id,
            'name': doctor.name,
            'consultation_room': doctor.consultation_room or '',
            'specialty': ', '.join(doctor.specialty_ids.mapped('name'))
        } for doctor in doctors]
    
    @http.route(['/appointments/booking/get_slots'], type='json', auth="public", website=True)
    def get_available_slots(self, doctor_id, date, **kw):
        """Obtiene slots disponibles para un doctor en una fecha (AJAX)"""
        doctor = request.env['hospital.doctor'].sudo().browse(int(doctor_id))
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = str(date_obj.weekday())
        
        # Buscar horarios del doctor para ese día
        schedules = request.env['hospital.schedule'].sudo().search([
            ('doctor_id', '=', doctor.id),
            ('day_of_week', '=', day_of_week),
            ('active', '=', True)
        ])
        
        if not schedules:
            return []
        
        slots = []
        for schedule in schedules:
            # Generar slots
            current_time = schedule.hour_from
            while current_time < schedule.hour_to:
                hour = int(current_time)
                minute = int((current_time - hour) * 60)
                slot_datetime = date_obj.replace(hour=hour, minute=minute)
                
                # Verificar si el slot está ocupado
                existing_appointments = request.env['hospital.appointment'].sudo().search_count([
                    ('doctor_id', '=', doctor.id),
                    ('appointment_date', '>=', slot_datetime),
                    ('appointment_date', '<', slot_datetime + timedelta(minutes=schedule.slot_duration)),
                    ('state', 'in', ['draft', 'confirmed', 'in_progress'])
                ])
                
                if existing_appointments == 0 and slot_datetime > datetime.now():
                    slots.append({
                        'time': slot_datetime.strftime('%H:%M'),
                        'datetime': slot_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'available': True
                    })
                
                current_time += schedule.slot_duration / 60.0
        
        return slots
    
    @http.route(['/appointments/booking/create'], type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def create_appointment(self, **post):
        """Crea una nueva cita desde el website"""
        try:
            # Buscar o crear paciente
            patient = request.env['hospital.patient'].sudo().search([
                ('identification_id', '=', post.get('identification_id'))
            ], limit=1)
            
            if not patient:
                # Crear nuevo paciente
                patient = request.env['hospital.patient'].sudo().create({
                    'name': post.get('patient_name'),
                    'identification_id': post.get('identification_id'),
                    'phone': post.get('phone'),
                    'email': post.get('email'),
                })
            
            # Crear cita
            appointment_datetime = datetime.strptime(post.get('appointment_datetime'), '%Y-%m-%d %H:%M:%S')
            
            appointment = request.env['hospital.appointment'].sudo().create({
                'patient_id': patient.id,
                'doctor_id': int(post.get('doctor_id')),
                'specialty_id': int(post.get('specialty_id')),
                'appointment_date': appointment_datetime,
                'reason': post.get('reason', ''),
                'state': 'draft',
            })
            
            return request.render("citas_hospital.website_booking_success", {
                'appointment': appointment,
            })
        
        except Exception as e:
            return request.render("citas_hospital.website_booking_error", {
                'error': str(e),
            })
