from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from workoutapi.models.workout_set import WorkoutSet
from workoutapi.models.workout_exercise import WorkoutExercise

class WorkoutSetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    class WorkoutSetSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkoutSet
            fields = ['id', 'workout_exercise', 'index', 'reps', 'weight', 'duration_seconds']

        def validate(self, attrs):
            attrs = super().validate(attrs)
            we = attrs.get('workout_exercise') or getattr(self.instance, 'workout_exercise', None)
            idx = attrs.get('index') or getattr(self.instance, 'index', None)
            if we and idx:
                qs = WorkoutSet.objects.filter(workout_exercise=we, index=idx)
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError({'index': f'Set {idx} already exists for this exercise.'})
            return attrs

    def _owned_qs(self, request):
        
        return WorkoutSet.objects.filter(
            workout_exercise__workout__user=request.user
        ).select_related('workout_exercise', 'workout_exercise__workout')

    def list(self, request):
        
        qs = self._owned_qs(request)
        we_id = request.query_params.get('workout_exercise')
        if we_id and we_id.isdigit():
            qs = qs.filter(workout_exercise_id=int(we_id))
        data = self.WorkoutSetSerializer(qs.order_by('workout_exercise_id', 'index', 'id'), many=True).data
        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            row = self._owned_qs(request).get(pk=pk)
        except WorkoutSet.DoesNotExist:
            return Response({'message': 'Set not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.WorkoutSetSerializer(row).data)

    @transaction.atomic
    def create(self, request):
        ser = self.WorkoutSetSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        we = ser.validated_data['workout_exercise']
        
        if we.workout.user != request.user:
            return Response({'message': 'Not authorized for this workout.'}, status=status.HTTP_403_FORBIDDEN)

        row = WorkoutSet.objects.create(**ser.validated_data)
        return Response(self.WorkoutSetSerializer(row).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, pk=None):
        partial = request.method.lower() == 'patch'
        try:
            row = self._owned_qs(request).get(pk=pk)
        except WorkoutSet.DoesNotExist:
            return Response({'message': 'Set not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = self.WorkoutSetSerializer(row, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        
        new_we = ser.validated_data.get('workout_exercise')
        if new_we and new_we.workout.user != request.user:
            return Response({'message': 'Not authorized for that workout.'}, status=status.HTTP_403_FORBIDDEN)

        for f, v in ser.validated_data.items():
            setattr(row, f, v)
        row.save()
        return Response(self.WorkoutSetSerializer(row).data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk)

    @transaction.atomic
    def destroy(self, request, pk=None):
        try:
            row = self._owned_qs(request).get(pk=pk)
        except WorkoutSet.DoesNotExist:
            return Response({'message': 'Set not found.'}, status=status.HTTP_404_NOT_FOUND)
        row.delete()
        return Response({'message': 'Set deleted.'})
