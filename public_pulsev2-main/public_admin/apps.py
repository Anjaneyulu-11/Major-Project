from django.apps import AppConfig


class PulseAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_admin'
    label = 'pulse_admin'
    verbose_name = 'Pulse Admin'