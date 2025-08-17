from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from workoutapi.models.workout import Workout
from workoutapi.models.workout_exercise import WorkoutExercise
from workoutapi.models.exercise import Exercise
from workoutapi.models.muscle_group import MuscleGroup

class WorkoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    model = Workout

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user).order_by('-date', '-id')
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def repeat(self, request, pk=None):

        try:
            original = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        clone = Workout.objects.create(
            user=request.user,
            title=original.title,
            date=timezone.now().date(),
            description=original.description,
            duration_minutes=original.duration_minutes,
            workout_type=original.workout_type,
            completed=False,
        )

        orig_rows = WorkoutExercise.objects.filter(workout=original).order_by('position', 'id')

        new_rows = [
            WorkoutExercise(
                workout=clone,
                exercise=row.exercise,
                position=row.position,
            )
            for row in orig_rows
        ]
        if new_rows:
            WorkoutExercise.objects.bulk_create(new_rows)


        return Response(self.WorkoutSerializer(clone).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='muscle-groups')
    def muscle_groups(self, request, pk=None):
        
        ex_ids = list(
            WorkoutExercise.objects
            .filter(workout_id=pk)
            .values_list('exercise_id', flat=True)
        )
        if not ex_ids:
            return Response([])

        groups = (
            MuscleGroup.objects
            .filter(exercisemusclegroup__exercise_id__in=ex_ids)
            .distinct()
            .values('id', 'name')
        )

        return Response(list(groups), status=status.HTTP_200_OK)

    class WorkoutSerializer(serializers.ModelSerializer):
        exercise_names = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Workout
            fields = [
                'id', 'title', 'date', 'description',
                'duration_minutes', 'workout_type', 'completed',
                'exercise_names',
            ]

        def get_exercise_names(self, obj):
            return list(
                Exercise.objects.filter(
                    workoutexercise__workout=obj
                ).values_list('name', flat=True).distinct()
            )

    @action(detail=True, methods=['post'], url_path='add-exercises')
    @transaction.atomic
    def add_exercises(self, request, pk=None):
        try:
            workout = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        ids = request.data if isinstance(request.data, list) else request.data.get('exercise_ids', [])
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return Response({'exercise_ids': ['Must be a list of integers.']}, status=status.HTTP_400_BAD_REQUEST)
        if not ids:
            return Response({'exercise_ids': ['Provide at least one exercise id.']}, status=status.HTTP_400_BAD_REQUEST)

        existing = set(Exercise.objects.filter(id__in=ids).values_list('id', flat=True))
        missing = sorted(set(ids) - existing)
        if missing:
            return Response({'exercise_ids': [f'Invalid ids: {missing}']}, status=status.HTTP_400_BAD_REQUEST)

        start = WorkoutExercise.objects.filter(workout=workout).aggregate(Max('position'))['position__max'] or 0

        rows = [
            WorkoutExercise(workout=workout, exercise_id=ex_id, position=start + idx)
            for idx, ex_id in enumerate(ids, start=1)
        ]
        WorkoutExercise.objects.bulk_create(rows)

        created = WorkoutExercise.objects.filter(workout=workout, position__gt=start).order_by('position')
        data = [
            {
                'id': we.id,
                'workout': we.workout_id,
                'exercise': we.exercise_id,
                'exercise_name': we.exercise.name if we.exercise_id else None,
                'position': we.position,
                'sets': we.sets,
                'reps': we.reps,
                'weight': we.weight,
                'duration_seconds': we.duration_seconds,
            }
        for we in created]
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        try:
            workout = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        workout.completed = True
        workout.save()
        return Response({'message': 'Workout marked complete.', 'completed': True}, status=status.HTTP_200_OK)

    def list(self, request):
        qs = self.get_queryset()
        return Response(self.WorkoutSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            workout = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.WorkoutSerializer(workout).data)

    def create(self, request):
        ser = self.WorkoutSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        workout = Workout.objects.create(
            user=request.user,
            title=ser.validated_data['title'],
            date=ser.validated_data['date'],
            description=ser.validated_data.get('description', ''),
            duration_minutes=ser.validated_data.get('duration_minutes', 0),
            workout_type=ser.validated_data.get('workout_type'),
            completed=ser.validated_data.get('completed', False),
        )
        return Response(self.WorkoutSerializer(workout).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        partial = request.method.lower() == 'patch'
        try:
            workout = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = self.WorkoutSerializer(workout, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        for field, value in ser.validated_data.items():
            setattr(workout, field, value)
        workout.save()
        return Response(self.WorkoutSerializer(workout).data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk)

    def destroy(self, request, pk=None):
        try:
            workout = self.get_queryset().get(pk=pk)
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        workout.delete()
        return Response({'message': 'Workout deleted.'}, status=status.HTTP_200_OK)
