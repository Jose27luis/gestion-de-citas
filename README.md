# Manual del Módulo Citas Hospital Santa Rosa
## Sistema de Gestión de Citas Médicas y Recetas para Odoo 18

**Versión:** 18.0.1.0.0
**Categoría:** Healthcare
**Autor:** Hospital Santa Rosa
**Licencia:** LGPL-3

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Desarrollo](#desarrollo)
4. [Base de Datos](#base-de-datos)
5. [Despliegue](#despliegue)
6. [Manual de Usuario](#manual-de-usuario)
7. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

El módulo **Citas Hospital Santa Rosa** es un sistema completo de gestión hospitalaria para Odoo 18 que permite:

- ✅ Gestión de pacientes con historial médico completo
- ✅ Administración de doctores y especialidades
- ✅ Programación y seguimiento de citas médicas
- ✅ Emisión y dispensación de recetas médicas
- ✅ Portal web para pacientes
- ✅ Dashboard de métricas y KPIs
- ✅ Notificaciones automáticas por email
- ✅ Reportes personalizados
- ✅ Sistema de seguridad por roles

---

## Instalación

### Requisitos Previos

**Requisitos del Sistema:**
- Odoo 18.0 (Community o Enterprise)
- Python 3.10+
- PostgreSQL 12+
- Sistema operativo: Linux (Ubuntu 20.04+ recomendado)

**Módulos de Odoo requeridos:**
- `base` - Módulo base de Odoo
- `mail` - Sistema de mensajería
- `calendar` - Gestión de calendario
- `web` - Framework web
- `hr` - Recursos humanos
- `portal` - Portal de clientes
- `website` - Sitio web
- `product` - Productos
- `stock` - Inventario

### Instalación Paso a Paso

#### 1. Copiar el módulo al directorio de addons

```bash
# Navegar al directorio de addons
cd /opt/odoo/odoo18/addons/

# Si el módulo ya existe, verificar permisos
sudo chown -R odoo:odoo citas_hospital
sudo chmod -R 755 citas_hospital
```

#### 2. Actualizar la lista de módulos en Odoo

```bash
# Reiniciar el servicio de Odoo
sudo systemctl restart odoo18

# O actualizar la lista de aplicaciones desde la interfaz:
# Aplicaciones > Actualizar lista de aplicaciones
```

#### 3. Instalar el módulo

**Desde la interfaz web:**
1. Iniciar sesión como administrador
2. Ir a **Aplicaciones**
3. Quitar el filtro "Aplicaciones"
4. Buscar "Citas Hospital Santa Rosa"
5. Hacer clic en **Instalar**

**Desde línea de comandos:**
```bash
sudo -u odoo /opt/odoo/odoo18/odoo-bin -c /etc/odoo18.conf \
  -d nombre_base_datos -i citas_hospital --stop-after-init
```

#### 4. Verificar la instalación

Después de la instalación, deberías ver:
- Nuevo menú "Hospital" en la barra superior
- Submenús: Pacientes, Doctores, Citas, Recetas, Dashboard
- Datos de demostración cargados (si se instaló con demo data)

### Configuración Inicial

#### 1. Configurar Grupos de Seguridad

Asignar usuarios a los grupos apropiados:
- **Hospital: Manager** - Acceso total
- **Hospital: Doctor** - Doctores
- **Hospital: Recepcionista** - Personal de recepción
- **Hospital: Farmacéutico** - Personal de farmacia
- **Hospital: Paciente** - Portal de pacientes

Ruta: `Configuración > Usuarios y Compañías > Usuarios`

#### 2. Configurar Especialidades

Ruta: `Hospital > Configuración > Especialidades`

Crear especialidades médicas (ejemplos):
- Cardiología (CARD)
- Pediatría (PEDI)
- Medicina General (MGEN)
- Traumatología (TRAU)

#### 3. Registrar Doctores

Ruta: `Hospital > Doctores > Doctores`

Para cada doctor, configurar:
- Datos personales
- Número de licencia médica
- Especialidades
- Horarios de atención
- Consultorio asignado

---

## Desarrollo

### Estructura del Módulo

```
citas_hospital/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── portal.py
├── data/
│   ├── sequences.xml
│   ├── mail_template.xml
│   ├── cron_jobs.xml
│   └── demo_data.xml
├── models/
│   ├── __init__.py
│   ├── hospital_patient.py
│   ├── hospital_doctor.py
│   ├── hospital_specialty.py
│   ├── hospital_appointment.py
│   ├── hospital_schedule.py
│   ├── hospital_prescription.py
│   ├── hospital_prescription_line.py
│   └── product_product.py
├── reports/
│   ├── prescription_report.xml
│   └── appointment_report.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── static/
│   ├── src/
│   │   ├── css/
│   │   │   ├── dashboard.css
│   │   │   └── website.css
│   │   └── js/
│   │       ├── appointment_booking.js
│   │       └── website_booking.js
│   └── description/
│       └── icon.png
├── views/
│   ├── hospital_patient_views.xml
│   ├── hospital_doctor_views.xml
│   ├── hospital_specialty_views.xml
│   ├── hospital_appointment_views.xml
│   ├── hospital_schedule_views.xml
│   ├── hospital_prescription_views.xml
│   ├── product_product_views.xml
│   ├── dashboard_views.xml
│   ├── portal_templates.xml
│   ├── website_templates.xml
│   └── menu.xml
└── wizard/
    ├── __init__.py
    └── appointment_cancel_wizard.py
```

### Modelos Principales

#### 1. `hospital.patient` - Pacientes

**Archivo:** `models/hospital_patient.py`

**Campos principales:**
- `name` - Nombre completo
- `identification_id` - DNI/Cédula (único)
- `birth_date` - Fecha de nacimiento
- `age` - Edad (calculada)
- `gender` - Género
- `blood_type` - Tipo de sangre
- `allergies` - Alergias
- `medical_history` - Historial médico

**Funcionalidades:**
- Cálculo automático de edad
- Creación automática de partner/contacto
- Smart buttons para citas y recetas
- Búsqueda inteligente por nombre, DNI o teléfono
- Validaciones de email y fecha de nacimiento

#### 2. `hospital.doctor` - Doctores

**Archivo:** `models/hospital_doctor.py`

**Campos principales:**
- `name` - Nombre completo
- `license_number` - Número de licencia médica (único)
- `specialty_ids` - Especialidades (many2many)
- `employee_id` - Empleado relacionado (HR)
- `consultation_room` - Consultorio
- `years_experience` - Años de experiencia

**Funcionalidades:**
- Relación con módulo HR
- Smart buttons para citas de hoy y pendientes
- Gestión de horarios de atención
- Contador de recetas emitidas

#### 3. `hospital.appointment` - Citas Médicas

**Archivo:** `models/hospital_appointment.py`

**Campos principales:**
- `name` - Número de cita (secuencia automática)
- `patient_id` - Paciente
- `doctor_id` - Doctor
- `specialty_id` - Especialidad
- `appointment_date` - Fecha y hora
- `state` - Estado (draft/confirmed/in_progress/done/cancelled)
- `reason` - Motivo de consulta

**Estados del flujo:**
1. **Borrador** → 2. **Confirmada** → 3. **En Progreso** → 4. **Realizada**
                  ↓
              **Cancelada**

**Funcionalidades:**
- Verificación de disponibilidad del doctor
- Creación automática de eventos en calendario
- Envío de emails de confirmación
- Recordatorios automáticos (24h y 2h antes)
- Cancelación automática de citas no confirmadas
- Wizard de cancelación con motivo
- Creación de receta desde la cita

#### 4. `hospital.prescription` - Recetas Médicas

**Archivo:** `models/hospital_prescription.py`

**Campos principales:**
- `name` - Número de receta (secuencia)
- `patient_id` - Paciente
- `doctor_id` - Doctor
- `appointment_id` - Cita relacionada
- `prescription_date` - Fecha de emisión
- `state` - Estado (draft/issued/dispensed/expired)
- `diagnosis` - Diagnóstico
- `line_ids` - Líneas de medicamentos
- `validity_days` - Días de validez (default 30)
- `expiry_date` - Fecha de expiración (calculada)

**Funcionalidades:**
- Verificación de stock de medicamentos
- Validación de expiración
- Impresión de receta en PDF
- Envío por email
- Acceso desde portal del paciente
- Marcado automático como expirada

#### 5. `hospital.specialty` - Especialidades

**Archivo:** `models/hospital_specialty.py`

**Campos principales:**
- `name` - Nombre
- `code` - Código único
- `appointment_duration` - Duración predeterminada de cita
- `color` - Color de identificación

#### 6. `hospital.schedule` - Horarios

**Archivo:** `models/hospital_schedule.py`

**Campos principales:**
- `doctor_id` - Doctor
- `day_of_week` - Día de la semana
- `hour_from` - Hora desde
- `hour_to` - Hora hasta
- `slot_duration` - Duración del slot

**Validaciones:**
- No solapamiento de horarios
- Horas válidas (0-24)
- Duración de slot positiva

### Seguridad y Permisos

#### Grupos de Seguridad

Definidos en `security/security.xml`:

1. **Hospital: Paciente (Portal)**
   - Acceso de portal
   - Solo ve sus propios datos

2. **Hospital: Recepcionista**
   - Usuario interno
   - Crea y gestiona citas
   - Gestiona pacientes

3. **Hospital: Doctor**
   - Hereda permisos de Recepcionista
   - Gestiona sus citas
   - Crea recetas

4. **Hospital: Farmacéutico**
   - Usuario interno
   - Dispensa recetas
   - Gestiona stock de medicamentos

5. **Hospital: Manager**
   - Acceso total
   - Configuración del sistema

#### Reglas de Registro (Record Rules)

**Pacientes:**
- Portal: Solo sus propios datos (lectura)
- Recepcionista+: Todos los pacientes (lectura, escritura, creación)
- Manager: Acceso completo incluyendo eliminación

**Citas:**
- Portal: Solo sus propias citas (lectura)
- Doctor: Solo sus citas (lectura, escritura)
- Recepcionista: Todas las citas (lectura, escritura, creación)
- Manager: Acceso completo

**Recetas:**
- Portal: Solo sus recetas (lectura)
- Doctor: Sus recetas (lectura, escritura, creación)
- Farmacéutico: Todas las recetas (lectura, escritura)
- Manager: Acceso completo

### Tareas Programadas (Cron Jobs)

Definidas en `data/cron_jobs.xml`:

1. **Recordatorios 24 horas antes**
   - Frecuencia: Cada hora
   - Función: `_cron_send_reminders_24h()`
   - Envía email a pacientes

2. **Recordatorios 2 horas antes**
   - Frecuencia: Cada 30 minutos
   - Función: `_cron_send_reminders_2h()`
   - Envía email y crea actividad para doctor

3. **Cancelación automática**
   - Frecuencia: Cada hora
   - Función: `_cron_auto_cancel_unconfirmed()`
   - Cancela citas no confirmadas 1 hora antes

4. **Marcado de recetas expiradas**
   - Frecuencia: Diaria
   - Función: `_cron_check_expiry()`
   - Marca recetas expiradas

### Plantillas de Email

Definidas en `data/mail_template.xml`:

1. `mail_template_appointment_confirmation` - Confirmación de cita
2. `mail_template_appointment_reminder_24h` - Recordatorio 24h
3. `mail_template_appointment_reminder_2h` - Recordatorio 2h
4. `mail_template_prescription_issued` - Receta emitida

### Reportes

#### 1. Reporte de Receta Médica
- Archivo: `reports/prescription_report.xml`
- Formato: PDF
- Incluye: Datos del paciente, doctor, diagnóstico, medicamentos, instrucciones

#### 2. Reporte de Cita
- Archivo: `reports/appointment_report.xml`
- Formato: PDF
- Incluye: Datos de la cita, paciente, doctor, especialidad

### Desarrollo de Nuevas Funcionalidades

#### Agregar un nuevo campo al modelo Patient

```python
# En models/hospital_patient.py

# 1. Agregar el campo
insurance_company = fields.Char(
    string='Compañía de Seguros',
    tracking=True
)

# 2. Actualizar la vista en views/hospital_patient_views.xml
<field name="insurance_company"/>

# 3. Agregar permisos si es necesario en security/ir.model.access.csv

# 4. Actualizar el módulo
sudo -u odoo /opt/odoo/odoo18/odoo-bin -c /etc/odoo18.conf \
  -d nombre_db -u citas_hospital --stop-after-init
```

#### Crear un nuevo wizard

```python
# En wizard/nuevo_wizard.py

from odoo import models, fields, api

class NuevoWizard(models.TransientModel):
    _name = 'nuevo.wizard'
    _description = 'Descripción del Wizard'

    campo1 = fields.Char(string='Campo 1', required=True)

    def action_confirmar(self):
        # Lógica del wizard
        return {'type': 'ir.actions.act_window_close'}
```

### Testing

#### Test Unitario de Ejemplo

```python
# En tests/test_appointment.py

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class TestAppointment(TransactionCase):

    def setUp(self):
        super(TestAppointment, self).setUp()

        # Crear datos de prueba
        self.patient = self.env['hospital.patient'].create({
            'name': 'Paciente Test',
            'identification_id': '12345678',
        })

        self.specialty = self.env['hospital.specialty'].create({
            'name': 'Cardiología',
            'code': 'CARD',
        })

        self.doctor = self.env['hospital.doctor'].create({
            'name': 'Dr. Test',
            'license_number': 'LIC001',
            'specialty_ids': [(6, 0, [self.specialty.id])],
        })

    def test_create_appointment(self):
        """Test creación de cita"""
        appointment = self.env['hospital.appointment'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'specialty_id': self.specialty.id,
            'appointment_date': datetime.now() + timedelta(days=1),
        })

        self.assertTrue(appointment.name)
        self.assertEqual(appointment.state, 'draft')

    def test_appointment_past_date(self):
        """Test validación de fecha pasada"""
        with self.assertRaises(ValidationError):
            self.env['hospital.appointment'].create({
                'patient_id': self.patient.id,
                'doctor_id': self.doctor.id,
                'specialty_id': self.specialty.id,
                'appointment_date': datetime.now() - timedelta(days=1),
            })
```

---

## Base de Datos

### Esquema de Base de Datos

#### Tabla: `hospital_patient`

```sql
CREATE TABLE hospital_patient (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    identification_id VARCHAR NOT NULL UNIQUE,
    birth_date DATE,
    age INTEGER,
    gender VARCHAR,
    blood_type VARCHAR,
    phone VARCHAR,
    email VARCHAR,
    address TEXT,
    partner_id INTEGER REFERENCES res_partner(id),
    allergies TEXT,
    medical_history TEXT,
    emergency_contact VARCHAR,
    emergency_phone VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    image_1920 BYTEA,
    create_date TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id)
);

CREATE INDEX idx_patient_identification ON hospital_patient(identification_id);
CREATE INDEX idx_patient_name ON hospital_patient(name);
```

#### Tabla: `hospital_doctor`

```sql
CREATE TABLE hospital_doctor (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    license_number VARCHAR NOT NULL UNIQUE,
    employee_id INTEGER REFERENCES hr_employee(id),
    phone VARCHAR,
    email VARCHAR,
    consultation_room VARCHAR,
    biography TEXT,
    years_experience INTEGER,
    active BOOLEAN DEFAULT TRUE,
    image_1920 BYTEA,
    color INTEGER,
    create_date TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id)
);

CREATE INDEX idx_doctor_license ON hospital_doctor(license_number);
CREATE INDEX idx_doctor_name ON hospital_doctor(name);
```

#### Tabla: `hospital_appointment`

```sql
CREATE TABLE hospital_appointment (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES hospital_patient(id),
    doctor_id INTEGER NOT NULL REFERENCES hospital_doctor(id),
    specialty_id INTEGER NOT NULL REFERENCES hospital_specialty(id),
    appointment_date TIMESTAMP NOT NULL,
    duration FLOAT DEFAULT 0.5,
    state VARCHAR NOT NULL DEFAULT 'draft',
    reason TEXT,
    notes TEXT,
    prescription_id INTEGER REFERENCES hospital_prescription(id),
    calendar_event_id INTEGER REFERENCES calendar_event(id),
    color INTEGER,
    confirmation_date TIMESTAMP,
    cancellation_reason TEXT,
    create_date TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id)
);

CREATE INDEX idx_appointment_date ON hospital_appointment(appointment_date);
CREATE INDEX idx_appointment_patient ON hospital_appointment(patient_id);
CREATE INDEX idx_appointment_doctor ON hospital_appointment(doctor_id);
CREATE INDEX idx_appointment_state ON hospital_appointment(state);
```

#### Tabla: `hospital_prescription`

```sql
CREATE TABLE hospital_prescription (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES hospital_patient(id),
    doctor_id INTEGER NOT NULL REFERENCES hospital_doctor(id),
    appointment_id INTEGER REFERENCES hospital_appointment(id),
    prescription_date DATE NOT NULL,
    state VARCHAR NOT NULL DEFAULT 'draft',
    diagnosis TEXT,
    general_instructions TEXT,
    validity_days INTEGER DEFAULT 30,
    expiry_date DATE,
    notes TEXT,
    create_date TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id)
);

CREATE INDEX idx_prescription_date ON hospital_prescription(prescription_date);
CREATE INDEX idx_prescription_patient ON hospital_prescription(patient_id);
CREATE INDEX idx_prescription_doctor ON hospital_prescription(doctor_id);
CREATE INDEX idx_prescription_state ON hospital_prescription(state);
```

### Secuencias

```sql
-- Secuencia para citas
CREATE SEQUENCE hospital_appointment_seq;
-- Formato: APT/2024/0001

-- Secuencia para recetas
CREATE SEQUENCE hospital_prescription_seq;
-- Formato: RX/2024/0001
```

### Backup y Restauración

#### Backup de Base de Datos

```bash
# Backup completo
sudo -u postgres pg_dump nombre_base_datos > backup_$(date +%Y%m%d).sql

# Backup comprimido
sudo -u postgres pg_dump nombre_base_datos | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup solo del módulo (datos)
sudo -u postgres pg_dump -t 'hospital_*' nombre_base_datos > backup_hospital_$(date +%Y%m%d).sql
```

#### Restauración

```bash
# Restaurar desde backup
sudo -u postgres psql nombre_base_datos < backup_20240101.sql

# Restaurar desde backup comprimido
gunzip -c backup_20240101.sql.gz | sudo -u postgres psql nombre_base_datos
```

#### Script de Backup Automático

```bash
#!/bin/bash
# backup_odoo.sh

DB_NAME="nombre_base_datos"
BACKUP_DIR="/opt/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Realizar backup
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_FILE

# Mantener solo los últimos 7 días
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_FILE"
```

Configurar en crontab:
```bash
# Ejecutar diariamente a las 2 AM
0 2 * * * /opt/scripts/backup_odoo.sh
```

### Consultas SQL Útiles

#### Estadísticas de Citas

```sql
-- Citas por estado
SELECT state, COUNT(*) as total
FROM hospital_appointment
GROUP BY state
ORDER BY total DESC;

-- Citas por doctor
SELECT d.name, COUNT(a.id) as total_citas
FROM hospital_doctor d
LEFT JOIN hospital_appointment a ON a.doctor_id = d.id
GROUP BY d.name
ORDER BY total_citas DESC;

-- Citas del día
SELECT a.name, p.name as paciente, d.name as doctor, a.appointment_date
FROM hospital_appointment a
JOIN hospital_patient p ON a.patient_id = p.id
JOIN hospital_doctor d ON a.doctor_id = d.id
WHERE DATE(a.appointment_date) = CURRENT_DATE
ORDER BY a.appointment_date;
```

#### Estadísticas de Pacientes

```sql
-- Pacientes por rango de edad
SELECT
    CASE
        WHEN age < 18 THEN 'Menor de 18'
        WHEN age BETWEEN 18 AND 30 THEN '18-30'
        WHEN age BETWEEN 31 AND 50 THEN '31-50'
        WHEN age BETWEEN 51 AND 70 THEN '51-70'
        ELSE 'Mayor de 70'
    END as rango_edad,
    COUNT(*) as total
FROM hospital_patient
WHERE active = TRUE
GROUP BY rango_edad
ORDER BY rango_edad;

-- Pacientes más frecuentes
SELECT p.name, p.identification_id, COUNT(a.id) as total_citas
FROM hospital_patient p
LEFT JOIN hospital_appointment a ON a.patient_id = p.id
GROUP BY p.id, p.name, p.identification_id
ORDER BY total_citas DESC
LIMIT 10;
```

---

## Despliegue

### Entorno de Producción

#### Requisitos de Hardware

**Servidor Mínimo:**
- CPU: 2 cores
- RAM: 4 GB
- Disco: 40 GB SSD
- Red: 10 Mbps

**Servidor Recomendado:**
- CPU: 4+ cores
- RAM: 8+ GB
- Disco: 100+ GB SSD
- Red: 100+ Mbps

#### Instalación en Producción

##### 1. Preparar el Sistema

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y postgresql postgresql-contrib \
    python3-pip python3-dev python3-venv \
    libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
    libfribidi-dev libxcb1-dev \
    nginx supervisor git
```

##### 2. Configurar PostgreSQL

```bash
# Crear usuario de base de datos
sudo -u postgres createuser -s odoo

# Crear base de datos
sudo -u postgres createdb -O odoo odoo_produccion

# Configurar autenticación
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Agregar: local   all   odoo   trust
```

##### 3. Instalar Odoo 18

```bash
# Crear usuario del sistema
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Clonar Odoo
sudo su - odoo
git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0 /opt/odoo/odoo18

# Crear entorno virtual
python3 -m venv /opt/odoo/odoo18-venv
source /opt/odoo/odoo18-venv/bin/activate

# Instalar dependencias
pip install wheel
pip install -r /opt/odoo/odoo18/requirements.txt
```

##### 4. Copiar el Módulo

```bash
# Copiar módulo al directorio de addons
sudo cp -r /ruta/origen/citas_hospital /opt/odoo/odoo18/addons/

# Ajustar permisos
sudo chown -R odoo:odoo /opt/odoo/odoo18/addons/citas_hospital
```

##### 5. Configurar Odoo

```bash
# Crear archivo de configuración
sudo nano /etc/odoo18.conf
```

Contenido:
```ini
[options]
; This is the password that allows database operations:
admin_passwd = admin_password_super_seguro
db_host = localhost
db_port = 5432
db_user = odoo
db_password = False
addons_path = /opt/odoo/odoo18/addons,/opt/odoo/odoo18/odoo/addons
logfile = /var/log/odoo18/odoo.log
log_level = info
xmlrpc_port = 8069
proxy_mode = True

; Configuraciones de producción
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
```

Ajustar permisos:
```bash
sudo chown odoo:odoo /etc/odoo18.conf
sudo chmod 640 /etc/odoo18.conf
```

##### 6. Configurar Systemd Service

```bash
sudo nano /etc/systemd/system/odoo18.service
```

Contenido:
```ini
[Unit]
Description=Odoo 18
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo18
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo18-venv/bin/python3 /opt/odoo/odoo18/odoo-bin -c /etc/odoo18.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable odoo18
sudo systemctl start odoo18
sudo systemctl status odoo18
```

##### 7. Configurar Nginx como Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/odoo
```

Contenido:
```nginx
# Upstream Odoo
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/odoo.crt;
    ssl_certificate_key /etc/ssl/private/odoo.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/odoo_access.log;
    error_log /var/log/nginx/odoo_error.log;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Increase proxy buffer size
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Increase max upload size
    client_max_body_size 100M;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;

    # Odoo
    location / {
        proxy_pass http://odoo;
    }

    # Longpolling
    location /longpolling {
        proxy_pass http://odoochat;
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Gzip
    gzip on;
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
}
```

Activar y reiniciar:
```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

##### 8. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Configurar renovación automática
sudo certbot renew --dry-run
```

##### 9. Instalar el Módulo en la Base de Datos

```bash
# Instalar módulo
sudo -u odoo /opt/odoo/odoo18-venv/bin/python3 /opt/odoo/odoo18/odoo-bin \
    -c /etc/odoo18.conf \
    -d odoo_produccion \
    -i citas_hospital \
    --stop-after-init
```

### Monitoreo y Mantenimiento

#### Logs

```bash
# Ver logs en tiempo real
sudo tail -f /var/log/odoo18/odoo.log

# Ver logs de nginx
sudo tail -f /var/log/nginx/odoo_access.log
sudo tail -f /var/log/nginx/odoo_error.log

# Ver logs de systemd
sudo journalctl -u odoo18 -f
```

#### Reiniciar Servicios

```bash
# Reiniciar Odoo
sudo systemctl restart odoo18

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

#### Actualizar el Módulo

```bash
# Actualizar código
sudo cp -r /ruta/nueva/version/citas_hospital /opt/odoo/odoo18/addons/
sudo chown -R odoo:odoo /opt/odoo/odoo18/addons/citas_hospital

# Actualizar en la base de datos
sudo -u odoo /opt/odoo/odoo18-venv/bin/python3 /opt/odoo/odoo18/odoo-bin \
    -c /etc/odoo18.conf \
    -d odoo_produccion \
    -u citas_hospital \
    --stop-after-init

# Reiniciar servicio
sudo systemctl restart odoo18
```

### Docker Deployment (Alternativa)

#### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    restart: always

  odoo:
    image: odoo:18.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
      - ./citas_hospital:/mnt/extra-addons/citas_hospital
    restart: always

volumes:
  odoo-web-data:
  odoo-db-data:
```

Ejecutar:
```bash
docker-compose up -d
```

---

## Manual de Usuario

### Roles y Permisos

El sistema define 5 roles principales:

1. **Paciente (Portal)** - Acceso limitado para pacientes
2. **Recepcionista** - Gestión de citas y pacientes
3. **Doctor** - Atención médica y emisión de recetas
4. **Farmacéutico** - Dispensación de medicamentos
5. **Manager** - Administración completa del sistema

### Guía para Recepcionistas

#### 1. Registrar un Nuevo Paciente

1. Ir a **Hospital > Pacientes > Pacientes**
2. Clic en **Crear**
3. Completar formulario:
   - **Nombre Completo** (obligatorio)
   - **DNI/Cédula** (obligatorio, único)
   - **Fecha de Nacimiento** (la edad se calcula automáticamente)
   - **Género**
   - **Tipo de Sangre**
   - **Teléfono** y **Email**
   - **Dirección**
   - **Alergias** (importante para el doctor)
   - **Contacto de Emergencia**
4. Clic en **Guardar**

**Notas:**
- El DNI/Cédula debe ser único en el sistema
- Si se proporciona email, se crea automáticamente un contacto asociado
- El paciente puede recibir acceso al portal para ver sus citas

#### 2. Programar una Cita

1. Ir a **Hospital > Citas > Citas**
2. Clic en **Crear**
3. Completar datos:
   - **Paciente**: Buscar por nombre o DNI
   - **Especialidad**: Seleccionar especialidad requerida
   - **Doctor**: Seleccionar doctor (solo aparecen doctores de esa especialidad)
   - **Fecha y Hora**: Seleccionar del calendario
   - **Duración**: Se precompleta según la especialidad
   - **Motivo de Consulta**: Descripción breve
4. Clic en **Guardar**
5. Clic en **Confirmar** para confirmar la cita

**Validaciones del sistema:**
- La fecha debe ser futura
- El doctor debe tener disponibilidad en ese horario
- El doctor debe tener la especialidad seleccionada

**Flujo de estados:**
```
Borrador → Confirmada → En Progreso → Realizada
              ↓
          Cancelada
```

#### 3. Cancelar una Cita

1. Abrir la cita a cancelar
2. Clic en **Cancelar**
3. Ingresar el motivo de cancelación en el wizard
4. Clic en **Confirmar Cancelación**

**Nota:** El sistema también cancela automáticamente citas no confirmadas 1 hora antes de su inicio.

#### 4. Búsqueda Rápida de Pacientes

El sistema permite buscar pacientes por:
- Nombre completo
- DNI/Cédula
- Teléfono

Simplemente escribir en el buscador y el sistema encontrará coincidencias.

### Guía para Doctores

#### 1. Ver Citas del Día

**Opción 1: Desde el Dashboard**
1. Ir a **Hospital > Dashboard**
2. Ver el widget "Mis Citas de Hoy"

**Opción 2: Desde la ficha del Doctor**
1. Ir a **Hospital > Doctores > Doctores**
2. Abrir su ficha de doctor
3. Clic en el smart button **"X Citas Hoy"**

#### 2. Atender una Cita

1. Abrir la cita desde la lista
2. Verificar datos del paciente:
   - Historial médico
   - Alergias (¡importante!)
   - Tipo de sangre
3. Clic en **Iniciar** para marcar la cita como "En Progreso"
4. Agregar notas de la consulta en el campo **Notas**
5. Al finalizar, clic en **Realizada**

#### 3. Crear una Receta

**Desde una cita:**
1. En la cita (estado "En Progreso" o "Realizada")
2. Clic en **Crear Receta**
3. Se abre formulario de receta precargado

**Receta independiente:**
1. Ir a **Hospital > Recetas > Recetas**
2. Clic en **Crear**
3. Seleccionar paciente y doctor

**Completar la receta:**
1. Ingresar **Diagnóstico**
2. Agregar **Líneas de Medicamentos**:
   - Clic en "Agregar una línea"
   - Seleccionar **Medicamento** (del catálogo de productos)
   - Ingresar **Cantidad**
   - Especificar **Dosis** (ej: "1 tableta cada 8 horas")
   - Agregar **Instrucciones** específicas
3. Ingresar **Instrucciones Generales** (HTML)
4. Configurar **Días de Validez** (default 30 días)
5. Clic en **Guardar**
6. Clic en **Emitir** para emitir la receta

**Estados de la receta:**
- **Borrador**: En edición
- **Emitida**: Lista para dispensar
- **Dispensada**: Medicamentos entregados
- **Expirada**: Pasó la fecha de validez

#### 4. Imprimir Receta

1. Abrir la receta
2. Clic en **Imprimir > Receta Médica**
3. Se genera PDF con:
   - Datos del paciente
   - Datos del doctor y licencia médica
   - Diagnóstico
   - Medicamentos con dosis e instrucciones
   - Instrucciones generales
   - Fecha de emisión y expiración

#### 5. Configurar Horarios de Atención

1. Ir a **Hospital > Doctores > Doctores**
2. Abrir su ficha
3. Ir a la pestaña **Horarios**
4. Clic en **Agregar una línea**
5. Configurar:
   - **Día de la Semana**
   - **Hora Desde** (formato 24h: 8.0 = 8:00, 14.5 = 14:30)
   - **Hora Hasta**
   - **Duración de Slot** (minutos, default 30)
6. Guardar

**Validaciones:**
- No puede haber solapamiento de horarios
- La hora de fin debe ser posterior al inicio

### Guía para Farmacéuticos

#### 1. Dispensar una Receta

1. Ir a **Hospital > Recetas > Recetas**
2. Filtrar por **Estado: Emitida**
3. Abrir la receta a dispensar
4. Verificar:
   - Fecha de expiración (debe estar vigente)
   - Disponibilidad de medicamentos en stock
5. Preparar los medicamentos según las líneas
6. Clic en **Dispensar**

**Nota:** El sistema no permitirá dispensar recetas expiradas.

#### 2. Ver Recetas del Día

```
Filtros: Estado = Emitida AND Fecha de Emisión = Hoy
```

#### 3. Gestionar Stock de Medicamentos

Los medicamentos se gestionan como productos de Odoo:

1. Ir a **Inventario > Productos > Productos**
2. Filtrar productos categorizados como "Medicamento"
3. Gestionar stock como cualquier producto de Odoo

### Guía para Pacientes (Portal)

Los pacientes con acceso al portal pueden:

#### 1. Acceder al Portal

1. Recibir email de invitación
2. Configurar contraseña
3. Ingresar a `https://tu-dominio.com/my/home`

#### 2. Ver Mis Citas

1. Ir a **Mis Citas**
2. Ver listado de citas:
   - Próximas citas
   - Historial de citas
   - Estado de cada cita
3. Ver detalles de cada cita

#### 3. Solicitar Cita desde el Sitio Web

1. Ir a `https://tu-dominio.com`
2. Clic en **Reservar Cita**
3. Completar formulario:
   - Seleccionar especialidad
   - Seleccionar doctor
   - Elegir fecha y hora
   - Ingresar motivo
4. Enviar solicitud
5. Esperar confirmación por email

#### 4. Ver Mis Recetas

1. Ir a **Mis Recetas**
2. Ver listado de recetas
3. Descargar PDF de cada receta
4. Ver estado:
   - Emitida (puede ser dispensada)
   - Dispensada (ya retirada)
   - Expirada

### Guía para Managers

#### 1. Dashboard y Métricas

1. Ir a **Hospital > Dashboard**
2. Ver métricas:
   - Citas del día
   - Citas pendientes
   - Recetas emitidas
   - Pacientes nuevos
   - Gráficos de tendencias

#### 2. Configurar Especialidades

1. Ir a **Hospital > Configuración > Especialidades**
2. Crear nueva especialidad:
   - **Nombre** (ej: Cardiología)
   - **Código** único (ej: CARD)
   - **Duración de Cita** predeterminada
   - **Color** para identificación visual
3. Guardar

#### 3. Gestionar Doctores

1. Ir a **Hospital > Doctores > Doctores**
2. Crear nuevo doctor:
   - Datos personales
   - **Número de Licencia Médica** (obligatorio, único)
   - Seleccionar **Especialidades** (puede tener varias)
   - Vincular con **Empleado** del módulo HR (opcional)
   - **Consultorio** asignado
   - Biografía (se muestra en web)
   - **Años de Experiencia**
3. Configurar **Horarios de Atención**
4. Guardar

#### 4. Gestionar Usuarios y Permisos

1. Ir a **Configuración > Usuarios y Compañías > Usuarios**
2. Crear/editar usuario
3. Asignar al grupo apropiado:
   - **Hospital: Manager** - Acceso total
   - **Hospital: Doctor** - Doctores
   - **Hospital: Recepcionista** - Recepción
   - **Hospital: Farmacéutico** - Farmacia
   - **Hospital: Paciente** - Portal

#### 5. Configurar Plantillas de Email

1. Ir a **Configuración > Técnico > Email > Plantillas de Email**
2. Editar plantillas existentes:
   - `mail_template_appointment_confirmation`
   - `mail_template_appointment_reminder_24h`
   - `mail_template_appointment_reminder_2h`
   - `mail_template_prescription_issued`
3. Personalizar asunto y contenido (soporta Qweb)

#### 6. Configurar Tareas Programadas

1. Ir a **Configuración > Técnico > Automatización > Acciones Programadas**
2. Ver/editar tareas:
   - **Recordatorios 24h**: Cada hora
   - **Recordatorios 2h**: Cada 30 minutos
   - **Cancelación automática**: Cada hora
   - **Marcado de recetas expiradas**: Diaria
3. Ajustar frecuencia según necesidades

#### 7. Reportes y Análisis

**Reportes disponibles:**

1. **Reporte de Citas**:
   - Ir a **Hospital > Citas > Reportes**
   - Aplicar filtros
   - Exportar a Excel o PDF

2. **Reporte de Recetas**:
   - Ir a **Hospital > Recetas > Reportes**
   - Filtrar por doctor, fecha, estado
   - Exportar datos

**Consultas SQL directas** (para administradores avanzados):
- Acceder a PostgreSQL
- Ejecutar consultas de la sección "Base de Datos"

### Notificaciones Automáticas

El sistema envía automáticamente:

#### 1. Confirmación de Cita
- **Cuándo:** Al confirmar una cita
- **A quién:** Paciente (email)
- **Contenido:** Datos de la cita, doctor, fecha/hora, ubicación

#### 2. Recordatorio 24 horas antes
- **Cuándo:** 24 horas antes de la cita
- **A quién:** Paciente
- **Contenido:** Recordatorio de cita próxima

#### 3. Recordatorio 2 horas antes
- **Cuándo:** 2 horas antes de la cita
- **A quién:** Paciente y Doctor
- **Contenido:**
  - Email al paciente
  - Actividad en Odoo para el doctor

#### 4. Receta Emitida
- **Cuándo:** Al emitir una receta
- **A quién:** Paciente
- **Contenido:** Notificación de receta lista, instrucciones

### Accesos Directos del Teclado

| Atajo | Acción |
|-------|--------|
| `Alt + C` | Crear nuevo registro |
| `Alt + S` | Guardar |
| `Alt + D` | Descartar |
| `Alt + E` | Editar |
| `Ctrl + K` | Buscar (Command Palette) |

### Mejores Prácticas

#### Para Recepcionistas
- ✅ Confirmar citas inmediatamente después de crearlas
- ✅ Verificar disponibilidad del doctor antes de agendar
- ✅ Mantener datos de contacto actualizados
- ✅ Incluir motivo de consulta para preparación del doctor

#### Para Doctores
- ✅ Revisar alergias antes de prescribir
- ✅ Documentar bien las notas de consulta
- ✅ Emitir recetas inmediatamente después de la consulta
- ✅ Mantener horarios de atención actualizados
- ✅ Marcar citas como "Realizada" al finalizar

#### Para Farmacéuticos
- ✅ Verificar fecha de expiración antes de dispensar
- ✅ Confirmar identidad del paciente
- ✅ Verificar disponibilidad de stock
- ✅ Marcar como "Dispensada" inmediatamente

#### Para Managers
- ✅ Revisar dashboard diariamente
- ✅ Mantener backup regular de la base de datos
- ✅ Revisar logs de errores semanalmente
- ✅ Actualizar el módulo cuando haya nuevas versiones
- ✅ Capacitar a usuarios nuevos

---

## Solución de Problemas

### Problemas Comunes

#### 1. No puedo instalar el módulo

**Síntomas:** El módulo no aparece en la lista de aplicaciones

**Soluciones:**
```bash
# Verificar que el módulo esté en el directorio correcto
ls -la /opt/odoo/odoo18/addons/citas_hospital

# Verificar permisos
sudo chown -R odoo:odoo /opt/odoo/odoo18/addons/citas_hospital
sudo chmod -R 755 /opt/odoo/odoo18/addons/citas_hospital

# Reiniciar Odoo
sudo systemctl restart odoo18

# Actualizar lista de aplicaciones desde la UI
# Aplicaciones > Actualizar lista de aplicaciones
```

#### 2. Error al confirmar cita: "El doctor ya tiene una cita"

**Causa:** Solapamiento de horarios

**Solución:**
- Verificar la agenda del doctor en vista de calendario
- Seleccionar otro horario disponible
- O seleccionar otro doctor de la misma especialidad

#### 3. No se envían emails de confirmación

**Verificaciones:**

```bash
# Verificar configuración de servidor de correo
# Ir a: Configuración > Técnico > Correo Electrónico > Servidores de Correo Saliente

# Probar conexión
# Clic en "Probar Conexión"

# Ver logs de email
# Configuración > Técnico > Correo Electrónico > Correos Electrónicos
```

**Configuración SMTP ejemplo (Gmail):**
- Servidor SMTP: smtp.gmail.com
- Puerto: 587
- Seguridad: TLS
- Usuario: tu_email@gmail.com
- Contraseña: Contraseña de aplicación

#### 4. Error al crear receta: "Debe agregar al menos un medicamento"

**Causa:** Intentar emitir receta sin líneas de medicamentos

**Solución:**
1. Agregar al menos una línea de medicamento
2. Luego clic en "Emitir"

#### 5. Portal del paciente no funciona

**Verificaciones:**
1. ¿El paciente tiene email configurado?
2. ¿Se creó el usuario de portal?
   - Ir al paciente > Partner Relacionado > Ver Partner
   - Ir a la pestaña "Usuario del Portal"
   - Activar "Usuario del Portal"
3. ¿Se envió la invitación?
   - Clic en "Enviar Email de Invitación de Portal"

#### 6. Citas no aparecen en el calendario

**Solución:**
- Verificar que la cita esté en estado "Confirmada"
- Solo las citas confirmadas crean eventos de calendario
- Verificar en: Calendario > Vista de Calendario

#### 7. Error 502 Bad Gateway (Nginx)

**Causas posibles:**
- Odoo no está ejecutándose
- Puerto incorrecto en configuración de Nginx

**Verificar:**
```bash
# Ver estado de Odoo
sudo systemctl status odoo18

# Si no está activo, iniciar
sudo systemctl start odoo18

# Ver logs
sudo tail -f /var/log/odoo18/odoo.log
```

#### 8. Base de datos muy lenta

**Optimizaciones:**

```sql
-- Reindexar base de datos
REINDEX DATABASE nombre_base_datos;

-- Vacuum
VACUUM ANALYZE;

-- Ver consultas lentas
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

#### 9. Módulo no se actualiza

**Forzar actualización:**
```bash
# Detener Odoo
sudo systemctl stop odoo18

# Actualizar módulo
sudo -u odoo /opt/odoo/odoo18-venv/bin/python3 /opt/odoo/odoo18/odoo-bin \
    -c /etc/odoo18.conf \
    -d nombre_bd \
    -u citas_hospital \
    --stop-after-init

# Iniciar Odoo
sudo systemctl start odoo18
```

### Logs y Debugging

#### Ver logs en tiempo real

```bash
# Odoo logs
sudo tail -f /var/log/odoo18/odoo.log

# Filtrar solo errores
sudo tail -f /var/log/odoo18/odoo.log | grep ERROR

# Nginx logs
sudo tail -f /var/log/nginx/odoo_error.log
```

#### Habilitar modo debug en Odoo

1. En la URL, agregar `?debug=1`:
   ```
   https://tu-dominio.com/web?debug=1
   ```

2. Ahora se verán:
   - Nombres técnicos de campos
   - IDs de registros
   - Más opciones en menús
   - Opción "Ver Metadatos"

#### Activar logs de SQL

En `/etc/odoo18.conf`:
```ini
[options]
log_level = debug_sql
```

Reiniciar Odoo para aplicar.

### Contacto y Soporte

**Desarrollador:** Hospital Santa Rosa
**Sitio Web:** https://www.hospitalsantarosa.com
**Email Soporte:** soporte@hospitalsantarosa.com

**Repositorio:**
- GitHub: [URL del repositorio si aplica]
- Reportar Issues: [URL de issues]

**Documentación Adicional:**
- Documentación oficial de Odoo: https://www.odoo.com/documentation/18.0/
- Foro de la comunidad: https://www.odoo.com/forum

---

## Changelog

### Versión 18.0.1.0.0 (Actual)

**Características:**
- ✅ Gestión completa de pacientes
- ✅ Gestión de doctores y especialidades
- ✅ Sistema de citas con calendario
- ✅ Emisión de recetas médicas
- ✅ Portal para pacientes
- ✅ Dashboard de métricas
- ✅ Notificaciones automáticas
- ✅ Reportes en PDF
- ✅ Sistema de seguridad por roles

**Módulos integrados:**
- Base, Mail, Calendar, Web
- HR (Recursos Humanos)
- Portal, Website
- Product, Stock

---

## Licencia

Este módulo se distribuye bajo licencia **LGPL-3**.

Copyright (c) 2024 Hospital Santa Rosa

---

## Anexos

### A. Glosario de Términos

- **Cita**: Encuentro programado entre paciente y doctor
- **Receta**: Prescripción médica de medicamentos
- **Especialidad**: Rama de la medicina (ej: Cardiología)
- **Portal**: Interfaz web para pacientes
- **Smart Button**: Botón con contador en la cabecera del formulario
- **Wizard**: Formulario emergente para acciones específicas
- **Cron**: Tarea programada que se ejecuta automáticamente

### B. Diagramas

#### Diagrama de Flujo de Cita

```
[Paciente llama]
    → [Recepcionista crea cita]
    → [Sistema valida disponibilidad]
    → [Recepcionista confirma]
    → [Sistema envía email confirmación]
    → [Sistema envía recordatorio 24h antes]
    → [Sistema envía recordatorio 2h antes]
    → [Doctor atiende cita]
    → [Doctor marca como Realizada]
    → [Doctor crea Receta (opcional)]
```

#### Diagrama de Flujo de Receta

```
[Doctor crea receta]
    → [Agrega medicamentos]
    → [Emite receta]
    → [Sistema envía email a paciente]
    → [Paciente va a farmacia]
    → [Farmacéutico verifica receta]
    → [Farmacéutico verifica stock]
    → [Farmacéutico dispensa]
    → [Sistema marca como Dispensada]
```

### C. Checklist de Implementación

- [ ] Servidor configurado (Linux, PostgreSQL, Nginx)
- [ ] Odoo 18 instalado
- [ ] Módulo citas_hospital copiado a addons
- [ ] Módulo instalado en base de datos
- [ ] Grupos de seguridad configurados
- [ ] Usuarios creados y asignados a grupos
- [ ] Especialidades médicas creadas
- [ ] Doctores registrados con sus especialidades
- [ ] Horarios de doctores configurados
- [ ] Servidor de correo (SMTP) configurado
- [ ] Plantillas de email personalizadas
- [ ] Certificado SSL instalado (Let's Encrypt)
- [ ] Nginx configurado como reverse proxy
- [ ] Backup automático configurado
- [ ] Datos de demostración eliminados (producción)
- [ ] Usuarios de portal activados para pacientes
- [ ] Sitio web configurado para reservas online
- [ ] Monitoreo de logs activado
- [ ] Usuarios capacitados en el sistema

### D. Comandos Útiles de Referencia Rápida

```bash
# Reiniciar Odoo
sudo systemctl restart odoo18

# Ver logs
sudo tail -f /var/log/odoo18/odoo.log

# Actualizar módulo
sudo -u odoo /opt/odoo/odoo18-venv/bin/python3 /opt/odoo/odoo18/odoo-bin \
    -c /etc/odoo18.conf -d DB_NAME -u citas_hospital --stop-after-init

# Backup de BD
sudo -u postgres pg_dump DB_NAME | gzip > backup_$(date +%Y%m%d).sql.gz

# Restaurar BD
gunzip -c backup.sql.gz | sudo -u postgres psql DB_NAME

# Renovar SSL
sudo certbot renew

# Ver status de servicios
sudo systemctl status odoo18 nginx postgresql
```

---

**Fin del Manual**

*Última actualización: 2024*
*Versión del manual: 1.0*
