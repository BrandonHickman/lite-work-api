from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from workoutapi.models.muscle_group import MuscleGroup

class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ['id', 'name']

class MuscleGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for muscle groups.
    """
    queryset = MuscleGroup.objects.all().order_by('id')
    serializer_class = MuscleGroupSerializer
    permission_classes = [IsAuthenticated]
