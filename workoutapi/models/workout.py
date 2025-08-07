from django.db import models
from django.contrib.auth.models import User
from .workout_type import WorkoutType

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField()
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.SET_NULL, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} on {self.date}"