from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from workoutapi.views.user import Users
from workoutapi.views.profile import ProfileViewSet
from workoutapi.views.auth import RegisterView, LoginView
from workoutapi.views.workout import WorkoutViewSet
from workoutapi.views.exercise import ExerciseViewSet
from workoutapi.views.workout_type import WorkoutTypeViewSet
from workoutapi.views.workout_exercise import WorkoutExerciseViewSet
from workoutapi.views.muscle_groups import MuscleGroupViewSet
from workoutapi.views.workout_set import WorkoutSetViewSet
from workoutapi.views.analytics import HeatmapView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', Users, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'workouts', WorkoutViewSet, basename='workout')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'workout-types', WorkoutTypeViewSet, basename='workouttype')
router.register(r'workout-exercises', WorkoutExerciseViewSet, basename='workoutexercise')
router.register(r'muscle-groups', MuscleGroupViewSet, basename='musclegroup')
router.register(r'workout-sets', WorkoutSetViewSet, basename='workout-set')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('analytics/heatmap/', HeatmapView.as_view(), name='heatmap'),
]

