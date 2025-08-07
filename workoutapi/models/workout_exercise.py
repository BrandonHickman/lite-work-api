from django.db import models
from .workout import Workout
from .exercise import Exercise


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.exercise.name} in {self.workout.title}"
