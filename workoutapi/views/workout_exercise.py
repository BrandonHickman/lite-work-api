from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from workoutapi.models import WorkoutExercise


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutExercise
        fields = [
            'id',
            'workout_id',
            'exercise_id',
            'sets',
            'reps',
            'weight',
            'duration_seconds'
        ]

class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [IsAuthenticated]