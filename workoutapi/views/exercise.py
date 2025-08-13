from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from workoutapi.models.exercise import Exercise
from workoutapi.models.muscle_group import MuscleGroup
from workoutapi.models.exercise_muscle_group import ExerciseMuscleGroup

class ExerciseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    class MuscleGroupMiniSerializer(serializers.ModelSerializer):
        class Meta:
            model = MuscleGroup
            fields = ['id', 'name']

    class ExerciseSerializer(serializers.ModelSerializer):
        # Read: show full muscle group objects
        muscle_groups = serializers.SerializerMethodField(read_only=True)
        # Write: accept list of muscle group IDs to attach
        muscle_group_ids = serializers.ListField(
            child=serializers.IntegerField(), write_only=True, required=False
        )

        class Meta:
            model = Exercise
            fields = ['id', 'name', 'category', 'description', 'muscle_groups', 'muscle_group_ids']

        def get_muscle_groups(self, obj):
            qs = MuscleGroup.objects.filter(exercisemusclegroup__exercise=obj).order_by('id')
            return ExerciseViewSet.MuscleGroupMiniSerializer(qs, many=True).data

    def get_queryset(self):
        qs = Exercise.objects.all().order_by('name', 'id')
        # Optional filter: /api/exercises?muscle_group=1,3
        ids_param = self.request.query_params.get('muscle_group')
        if ids_param:
            try:
                ids = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
                if ids:
                    qs = qs.filter(exercisemusclegroup__muscle_group_id__in=ids).distinct()
            except ValueError:
                pass
        return qs

    def list(self, request):
        data = self.ExerciseSerializer(self.get_queryset(), many=True).data
        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            exercise = self.get_queryset().get(pk=pk)
        except Exercise.DoesNotExist:
            return Response({'message': 'Exercise not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.ExerciseSerializer(exercise).data)

    @transaction.atomic
    def create(self, request):
        ser = self.ExerciseSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create the exercise
        exercise = Exercise.objects.create(
            name=ser.validated_data['name'],
            category=ser.validated_data.get('category', ''),
            description=ser.validated_data.get('description', '')
        )

        # Attach muscle groups if provided
        mg_ids = ser.validated_data.get('muscle_group_ids', [])
        if mg_ids:
            # Validate ids exist
            existing_ids = set(MuscleGroup.objects.filter(id__in=mg_ids).values_list('id', flat=True))
            missing = set(mg_ids) - existing_ids
            if missing:
                return Response({'muscle_group_ids': [f'Invalid ids: {sorted(missing)}']},
                                status=status.HTTP_400_BAD_REQUEST)
            # Bulk create join rows
            ExerciseMuscleGroup.objects.bulk_create(
                [ExerciseMuscleGroup(exercise=exercise, muscle_group_id=mg_id) for mg_id in existing_ids]
            )

        return Response(self.ExerciseSerializer(exercise).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, pk=None):
        partial = request.method.lower() == 'patch'
        try:
            exercise = self.get_queryset().get(pk=pk)
        except Exercise.DoesNotExist:
            return Response({'message': 'Exercise not found.'}, status=status.HTTP_404_NOT_FOUND)

        ser = self.ExerciseSerializer(exercise, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update basic fields
        for field in ['name', 'category', 'description']:
            if field in ser.validated_data:
                setattr(exercise, field, ser.validated_data[field])
        exercise.save()

        # If muscle_group_ids provided, replace associations
        if 'muscle_group_ids' in ser.validated_data:
            new_ids = set(ser.validated_data['muscle_group_ids'])
            existing_ids = set(MuscleGroup.objects.filter(id__in=new_ids).values_list('id', flat=True))
            missing = new_ids - existing_ids
            if missing:
                return Response({'muscle_group_ids': [f'Invalid ids: {sorted(missing)}']},
                                status=status.HTTP_400_BAD_REQUEST)

            # Current links
            current_ids = set(
                ExerciseMuscleGroup.objects.filter(exercise=exercise).values_list('muscle_group_id', flat=True)
            )
            to_add = existing_ids - current_ids
            to_remove = current_ids - existing_ids

            if to_remove:
                ExerciseMuscleGroup.objects.filter(exercise=exercise, muscle_group_id__in=to_remove).delete()
            if to_add:
                ExerciseMuscleGroup.objects.bulk_create(
                    [ExerciseMuscleGroup(exercise=exercise, muscle_group_id=mg_id) for mg_id in to_add]
                )

        return Response(self.ExerciseSerializer(exercise).data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk)

    def destroy(self, request, pk=None):
        try:
            exercise = self.get_queryset().get(pk=pk)
        except Exercise.DoesNotExist:
            return Response({'message': 'Exercise not found.'}, status=status.HTTP_404_NOT_FOUND)
        exercise.delete()  # cascades remove join rows
        return Response({'message': 'Exercise deleted.'}, status=status.HTTP_200_OK)
