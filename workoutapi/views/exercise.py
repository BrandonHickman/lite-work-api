from rest_framework import serializers, viewsets
from workoutapi.models import Exercise


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()

    class ExerciseSerializer(serializers.ModelSerializer):
        class Meta:
            model = Exercise
            fields = [
                'id',
                'name',
                'category',
                'description'
            ]

    serializer_class = ExerciseSerializer