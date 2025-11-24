/** @odoo-module **/

// Website booking functionality
(function() {
    'use strict';

    // Cuando cambia la especialidad, cargar doctores
    $('#specialty_id').on('change', function() {
        var specialtyId = $(this).val();
        if (specialtyId) {
            $.ajax({
                url: '/appointments/booking/get_doctors',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {specialty_id: specialtyId}
                }),
                success: function(response) {
                    var doctors = response.result;
                    var $doctorSelect = $('#doctor_id');
                    $doctorSelect.empty().append('<option value="">-- Seleccione --</option>');
                    doctors.forEach(function(doctor) {
                        $doctorSelect.append($('<option>', {
                            value: doctor.id,
                            text: doctor.name
                        }));
                    });
                    $doctorSelect.prop('disabled', false);
                }
            });
        }
    });

    // Cuando cambia el doctor, habilitar fecha
    $('#doctor_id').on('change', function() {
        if ($(this).val()) {
            $('#appointment_date').prop('disabled', false);
        }
    });

    // Cuando cambia la fecha, cargar slots disponibles
    $('#appointment_date').on('change', function() {
        var doctorId = $('#doctor_id').val();
        var date = $(this).val();
        if (doctorId && date) {
            $.ajax({
                url: '/appointments/booking/get_slots',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {doctor_id: doctorId, date: date}
                }),
                success: function(response) {
                    var slots = response.result;
                    var $timeSelect = $('#appointment_time');
                    $timeSelect.empty();
                    if (slots.length === 0) {
                        $timeSelect.append('<option value="">No hay horarios disponibles</option>');
                    } else {
                        $timeSelect.append('<option value="">-- Seleccione --</option>');
                        slots.forEach(function(slot) {
                            $timeSelect.append($('<option>', {
                                value: slot.datetime,
                                text: slot.time
                            }));
                        });
                    }
                    $timeSelect.prop('disabled', false);
                }
            });
        }
    });
})();
