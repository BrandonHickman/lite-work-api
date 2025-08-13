from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from workoutapi.models.workout import Workout

class WorkoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    class WorkoutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Workout
            fields = [
                'id', 'title', 'date', 'description',
                'duration_minutes', 'workout_type', 'completed'
            ]

    def get_queryset(self):
        # Only the current user's workouts
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

        # Force ownership to the logged-in user
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
            workout = self.get_queryset().get(pk=pk)  # ensures ownership
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
