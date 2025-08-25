#!/bin/bash

# Script de inicio para Render
# Detecta si estamos en un entorno de Render (con variable PORT)
if [ -n "$PORT" ]; then
    # Entorno de producción - usar Gunicorn
    echo "Iniciando aplicación con Gunicorn en puerto $PORT"
    gunicorn produccion.wsgi:application --bind 0.0.0.0:$PORT
else
    # Entorno de desarrollo - usar runserver
    echo "Iniciando aplicación con runserver"
    python manage.py runserver 0.0.0.0:8000
fi
