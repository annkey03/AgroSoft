# Guía de Configuración - Recuperación de Contraseña por Email

## Resumen de Cambios Realizados

✅ **Implementación completa de recuperación de contraseña por email**

### Archivos Modificados:
1. `produccion/settings.py` - Configuración de email SMTP
2. `usuarios/models.py` - Agregados campos `reset_token` y `reset_token_expires`
3. `usuarios/views.py` - Actualizadas las vistas `recuperar_contrasena` y `cambiar_contrasena`
4. `usuarios/templates/email_recuperacion.html` - Template de email HTML
5. `usuarios/templates/recuperar_contrasena.html` - Actualizado para buscar por username o email

### Nuevos Archivos:
- `usuarios/templates/email_recuperacion.html` - Template de email
- `produccion/email_config.py` - Guía de configuración de email

## Configuración de Email

### Opción 1: Desarrollo (Consola)
Para pruebas en desarrollo, los emails se mostrarán en la consola:

```python
# En produccion/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Opción 2: Gmail (Producción)
1. Ve a https://myaccount.google.com/security
2. Activa "Verificación en dos pasos"
3. Crea una "Contraseña de
