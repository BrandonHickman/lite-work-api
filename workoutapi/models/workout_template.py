from django.db import models
from workoutapi.models.exercise import Exercise

class WorkoutTemplate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

class WorkoutTemplateExercise(models.Model):
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name='rows')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['position', 'id']
