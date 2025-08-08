from rest_framework import viewsets, serializers
from workoutapi.models import Workout

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()

    class WorkoutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Workout
            fields = [
                'id',
                'user',
                'title',
                'date',
                'description',
                'duration_minutes',
                'workout_type',
                'completed'
            ]

    serializer_class = WorkoutSerializer

