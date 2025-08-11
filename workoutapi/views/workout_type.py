from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from workoutapi.models import WorkoutType

class WorkoutTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutType
        fields = [
            'id',
            'name'
        ]

class WorkoutTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkoutType.objects.all()
    serializer_class = WorkoutTypeSerializer
    permission_classes = [IsAuthenticated]