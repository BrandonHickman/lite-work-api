from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from workoutapi.models import Workout

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

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

