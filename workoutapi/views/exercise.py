from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from workoutapi.models.exercise import Exercise
from workoutapi.models.muscle_group import MuscleGroup
from workoutapi.models.exercise_muscle_group import ExerciseMuscleGroup

class MuscleGroupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ['id', 'name']

class ExerciseSerializer(serializers.ModelSerializer):
    muscle_groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'description', 'muscle_groups']

    def get_muscle_groups(self, obj):
        qs = MuscleGroup.objects.filter(exercisemusclegroup__exercise=obj).order_by('id')
        return MuscleGroupMiniSerializer(qs, many=True).data

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        qs = Exercise.objects.all().order_by('name', 'id')
        ids_param = self.request.query_params.get('muscle_group')
        if ids_param:
            ids = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
            if ids:
                qs = qs.filter(exercisemusclegroup__muscle_group_id__in=ids).distinct()
        return qs
