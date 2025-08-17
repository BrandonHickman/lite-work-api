from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Max
from workoutapi.models.workout_exercise import WorkoutExercise
from workoutapi.models.workout import Workout
from workoutapi.models.exercise import Exercise

class WorkoutExerciseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    class WorkoutExerciseSerializer(serializers.ModelSerializer):
        workout  = serializers.PrimaryKeyRelatedField(queryset=Workout.objects.all())
        exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all())
        exercise_name = serializers.SerializerMethodField()

        class Meta:
            model = WorkoutExercise
            fields = [
                'id', 'workout', 'exercise',
                'sets', 'reps', 'weight', 'duration_seconds',
                'position', 'workout_sets', 'exercise_name'
            ]
            
            validators = []
            
            extra_kwargs = {
                'position': {'required': False}
            }

        def validate(self, attrs):

            workout  = attrs.get('workout')  or getattr(self.instance, 'workout',  None)
            position = attrs.get('position') or getattr(self.instance, 'position', None)

            if position is not None and workout is not None:
                qs = WorkoutExercise.objects.filter(workout=workout, position=position)
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError(
                        {'position': f'Position {position} is already used in this workout.'}
                    )
            return attrs
        
        def get_exercise_name(self, obj):
            return getattr(obj.exercise, 'name', None)


    

    def get_queryset(self):
        return WorkoutExercise.objects.filter(
            workout__user=self.request.user
        ).select_related('workout', 'exercise')

    def list(self, request):
        qs = self.get_queryset()
        workout_id = request.query_params.get('workout')
        if workout_id and workout_id.isdigit():
            qs = qs.filter(workout_id=int(workout_id))
        return Response(self.WorkoutExerciseSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            row = self.get_queryset().get(pk=pk)
        except WorkoutExercise.DoesNotExist:
            return Response({'message': 'Workout exercise not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.WorkoutExerciseSerializer(row).data)

    @transaction.atomic
    def create(self, request):
        ser = self.WorkoutExerciseSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        workout = ser.validated_data['workout']
        exercise = ser.validated_data['exercise']

        if workout.user != request.user:
            return Response({'message': 'Not authorized to modify this workout.'},
                            status=status.HTTP_403_FORBIDDEN)

        pos = ser.validated_data.get('position')
        if pos is None:
            max_pos = WorkoutExercise.objects.filter(workout=workout).aggregate(Max('position'))['position__max'] or 0
            pos = max_pos + 1

        row = WorkoutExercise.objects.create(
            workout=workout,
            exercise=exercise,
            sets=ser.validated_data.get('sets'),
            reps=ser.validated_data.get('reps'),
            weight=ser.validated_data.get('weight'),
            duration_seconds=ser.validated_data.get('duration_seconds'),
            position=pos,
        )
        return Response(self.WorkoutExerciseSerializer(row).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, pk=None):
        partial = request.method.lower() == 'patch'
        try:
            row = self.get_queryset().get(pk=pk)
        except WorkoutExercise.DoesNotExist:
            return Response({'message': 'Workout exercise not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = self.WorkoutExerciseSerializer(row, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        if 'workout' in ser.validated_data:
            new_workout = ser.validated_data['workout']
            if new_workout.user != request.user:
                return Response({'message': 'Not authorized to move to that workout.'},
                                status=status.HTTP_403_FORBIDDEN)
            row.workout = new_workout

        for field in ['exercise', 'sets', 'reps', 'weight', 'duration_seconds', 'position']:
            if field in ser.validated_data:
                setattr(row, field, ser.validated_data[field])

        if row.position is None:
            max_pos = WorkoutExercise.objects.filter(workout=row.workout).aggregate(Max('position'))['position__max'] or 0
            row.position = max_pos + 1

        row.save()
        return Response(self.WorkoutExerciseSerializer(row).data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk)

    def destroy(self, request, pk=None):
        try:
            row = self.get_queryset().get(pk=pk)
        except WorkoutExercise.DoesNotExist:
            return Response({'message': 'Workout exercise not found.'}, status=status.HTTP_404_NOT_FOUND)

        row.delete()
        return Response({'message': 'Workout exercise deleted.'}, status=status.HTTP_200_OK)
