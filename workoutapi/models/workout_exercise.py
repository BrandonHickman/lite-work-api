from django.db import models
from .workout import Workout
from .exercise import Exercise

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(null=True, blank=True)
    reps = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    position = models.PositiveIntegerField(default=1)

    class Meta:
        # Always return rows ordered within each workout
        ordering = ['workout_id', 'position', 'id']
        # If you want to prevent two rows having the same position in one workout, uncomment: Recommended to enforce unique position per workout to avoid weird ordering bugs and keeps UI predictable.
        constraints = [
            models.UniqueConstraint(fields=['workout', 'position'], name='uniq_workout_position')
        ]

    def __str__(self):
        return f"{self.workout_id} • {self.exercise_id} • pos {self.position}"
