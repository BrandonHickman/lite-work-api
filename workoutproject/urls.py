from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from workoutapi.views.register import RegisterView, LoginView

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
]

