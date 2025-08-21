from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from workoutapi.models.workout_template import WorkoutTemplate, WorkoutTemplateExercise
from workoutapi.models.workout import Workout
from workoutapi.models.workout_exercise import WorkoutExercise
from workoutapi.models.exercise import Exercise

class WorkoutTemplateSerializer(serializers.ModelSerializer):
    exercise_names = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutTemplate
        fields = ['id', 'title', 'description', 'exercise_names']

    def get_exercise_names(self, obj):
        return list(
            Exercise.objects.filter(workouttemplateexercise__template=obj)
            .values_list('name', flat=True).distinct()
        )

class WorkoutTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = WorkoutTemplate.objects.all().order_by('id')
    serializer_class = WorkoutTemplateSerializer

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        template = self.get_object()

        clone = Workout.objects.create(
            user=request.user,
            title=template.title,
            date=timezone.now().date(),
            description=template.description,
            duration_minutes=0,
            workout_type=None,
            completed=False,
        )

        rows = []
        for r in WorkoutTemplateExercise.objects.filter(template=template).order_by('position', 'id'):
            rows.append(WorkoutExercise(workout=clone, exercise=r.exercise, position=r.position))
        if rows:
            WorkoutExercise.objects.bulk_create(rows)

        from workoutapi.views.workout import WorkoutViewSet
        return Response(WorkoutViewSet.WorkoutSerializer(clone).data, status=status.HTTP_201_CREATED)
