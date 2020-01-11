from django.apps import AppConfig


class CardConfig(AppConfig):
    name = 'online.card'
    verbose_name = 'online.card'

    def ready(self):
        # improt signal handlers
        import online.card.signals
