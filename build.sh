#!/bin/bash

# Activar el entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Recoger archivos estáticos
python manage.py collectstatic --noinput

# Iniciar el servidor
gunicorn produccion.wsgi:application --bind 0.0.0.0:8000
