from django.apps import AppConfig


class MandalartsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mandalarts'
    def ready(self):
        import mandalarts.signals
