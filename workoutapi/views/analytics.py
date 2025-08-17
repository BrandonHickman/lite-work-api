from datetime import date, timedelta
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from workoutapi.models.workout import Workout

class HeatmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = date.today() - timedelta(days=365)
        qs = (Workout.objects
              .filter(user=request.user, completed=True, date__gte=start)
              .values('date')
              .annotate(count=Count('id')))
        out = {str(row['date']): row['count'] for row in qs}
        return Response(out)
