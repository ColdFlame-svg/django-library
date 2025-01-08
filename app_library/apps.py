from django.apps import AppConfig

class AppLibraryConfig(AppConfig):
    name = 'app_library'

    def ready(self):
        import app_library.signals  # Ensure this matches the name of your app
