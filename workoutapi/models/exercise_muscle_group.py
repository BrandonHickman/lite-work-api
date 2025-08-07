from django.db import models
from .exercise import Exercise
from .muscle_group import MuscleGroup

class ExerciseMuscleGroup(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.exercise.name} - {self.muscle_group.name}"