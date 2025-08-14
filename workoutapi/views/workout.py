from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Max
from workoutapi.models.workout import Workout
from workoutapi.models.workout_exercise import WorkoutExercise
from workoutapi.models.exercise import Exercise


class WorkoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def add_exercises(self, request, pk=None):
        """
        Bulk-append exercises to this workout.
        Body: { "exercise_ids": [1,2,3] }
        Appends at end: position = (current max) + 1, +2, ...
        """

        try:
            workout = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist if hasattr(self, 'model') else Exception:
        
            try:
                workout = self.get_queryset().get(pk=pk)
            except:
                return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        
        ids = request.data.get('exercise_ids', [])
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return Response({'exercise_ids': ['Must be a list of integers.']}, status=status.HTTP_400_BAD_REQUEST)
        if not ids:
            return Response({'exercise_ids': ['Provide at least one exercise id.']}, status=status.HTTP_400_BAD_REQUEST)

        
        existing = set(Exercise.objects.filter(id__in=ids).values_list('id', flat=True))
        missing = sorted(set(ids) - existing)
        if missing:
            return Response({'exercise_ids': [f'Invalid ids: {missing}']}, status=status.HTTP_400_BAD_REQUEST)

        
        start = WorkoutExercise.objects.filter(workout=workout).aggregate(
            Max('position')
        )['position__max'] or 0

        
        rows = []
        for offset, ex_id in enumerate(ids, start=1):
            rows.append(WorkoutExercise(
                workout=workout,
                exercise_id=ex_id,
                position=start + offset
            ))
        WorkoutExercise.objects.bulk_create(rows)

       
        from workoutapi.views.workout_exercise import WorkoutExerciseViewSet 
        created = WorkoutExercise.objects.filter(workout=workout, position__gt=start).order_by('position')
        return Response(
            WorkoutExerciseViewSet.WorkoutExerciseSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Marks the workout as completed=true.
        """
        try:
            workout = self.get_queryset().get(pk=pk) 
        except:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        workout.completed = True
        workout.save()
        return Response({'message': 'Workout marked complete.', 'completed': True}, status=status.HTTP_200_OK)


    class WorkoutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Workout
            fields = [
                'id', 'title', 'date', 'description',
                'duration_minutes', 'workout_type', 'completed'
            ]

    def get_queryset(self):
        
        return Workout.objects.filter(user=self.request.user).order_by('-date', '-id')

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
        serializer = self.WorkoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        workout = Workout.objects.create(
            user=request.user,
            title=serializer.validated_data['title'],
            date=serializer.validated_data['date'],
            description=serializer.validated_data.get('description', ''),
            duration_minutes=serializer.validated_data['duration_minutes'],
            workout_type=serializer.validated_data.get('workout_type'),
            completed=serializer.validated_data.get('completed', False),
        )
        return Response(self.WorkoutSerializer(workout).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        partial = request.method.lower() == 'patch'
        try:
            workout = self.get_queryset().get(pk=pk) 
        except Workout.DoesNotExist:
            return Response({'message': 'Workout not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.WorkoutSerializer(workout, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for field, value in serializer.validated_data.items():
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
