from django.apps import AppConfig

class WorkoutapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workoutapi'

    def ready(self):
        import workoutapi.signals
