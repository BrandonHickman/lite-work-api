from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from workoutapi.models.exercise import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'category', 'description'
        ]

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]