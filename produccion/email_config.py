"""
Configuración de email para desarrollo
Para usar en producción, configura las variables de entorno
"""

# Configuración para desarrollo usando consola (no envía emails reales)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración para Gmail (descomenta y configura para usar en producción)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-correo@gmail.com'  # Cambiar esto
EMAIL_HOST_PASSWORD = 'tu-contraseña-de-app'  # Cambiar esto
DEFAULT_FROM_EMAIL = 'tu-correo@gmail.com'

# Para obtener la contraseña de app de Gmail:
# 1. Ve a https://myaccount.google.com/security
# 2. Activa "Verificación en dos pasos"
# 3. Crea una "Contraseña de aplicación"
