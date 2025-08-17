from django.db import models
from workoutapi.models.workout_exercise import WorkoutExercise

class WorkoutSet(models.Model):
    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='workout_sets'
    )
    index = models.PositiveIntegerField()

    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['workout_exercise_id', 'index', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['workout_exercise', 'index'],
                name='uniq_workout_exercise_set_index'
            )
        ]

    def __str__(self):
        return f"WE#{self.workout_exercise_id} – Set {self.index}"
