from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from workoutapi.models.workout import Workout


class HeatmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns { "YYYY-MM-DD": count } for the past N days (default 365)
        counting the user's completed workouts per day.
        Optional query param: ?days=180  (min 7, max 730)
        """
        try:
            days = int(request.query_params.get("days", 365))
        except (TypeError, ValueError):
            days = 365
        days = max(7, min(days, 730))

        end = timezone.localdate()
        start = end - timedelta(days=days - 1)

        qs = (
            Workout.objects
            .filter(user=request.user, completed=True, date__gte=start, date__lte=end)
            .values("date")
            .annotate(c=Count("id"))
        )

        data = {row["date"].isoformat(): row["c"] for row in qs}
        return Response(data)
