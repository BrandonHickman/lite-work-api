from rest_framework import serializers, viewsets
from workoutapi.models import WorkoutExercise


class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()

    class WorkoutExerciseSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkoutExercise
            fields = [
                'id',
                'workout',
                'exercise',
                'sets',
                'reps',
                'weight',
                'duration_seconds'
            ]
    
    serializer_class = WorkoutExerciseSerializer