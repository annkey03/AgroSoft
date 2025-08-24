#!/bin/bash

# Instalar dependencias
poetry install --no-dev

# Ejecutar migraciones
poetry run python manage.py migrate

# Recoger archivos estáticos
poetry run python manage.py collectstatic --noinput
