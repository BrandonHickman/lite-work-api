from rest_framework import viewsets, serializers
from workoutapi.models import WorkoutType

class WorkoutTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkoutType.objects.all()

    class WorkoutTypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkoutType
            fields = [
                'id',
                'name'
            ]

    serializer_class = WorkoutTypeSerializer