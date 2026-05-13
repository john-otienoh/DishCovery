from django.apps import AppConfig


class InteractionsConfig(AppConfig):
    name = 'apps.interactions'
    def ready(self):
        import apps.interactions.signals
        