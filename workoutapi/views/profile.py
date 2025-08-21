from rest_framework import serializers, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseServerError
from workoutapi.models.profile import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'created_at', 'avatar', 'challenge_goal', 'challenge_started_at', 'challenge_window_days', 'challenge_label'
        ]
        read_only_fields = ['created_at', 'username', 'email', 'first_name', 'last_name']

class ProfileViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        profile = request.user.profile
        if request.method.lower() == 'get':
            return Response(ProfileSerializer(profile).data)
        ser = ProfileSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)

    def list(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        profile = request.user.profile
        return Response(ProfileSerializer(profile).data)

    def update(self, request, pk=None):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if profile.user != request.user:
            return Response({'message': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        partial = request.method.lower() == 'patch'
        serializer = ProfileSerializer(profile, data=request.data, partial=partial)
        if serializer.is_valid():
            profile.bio = serializer.validated_data.get('bio', profile.bio)
            profile.profile_image_url = serializer.validated_data.get('profile_image_url', profile.profile_image_url)
            profile.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        profile = request.user.profile
        ser = ProfileSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def destroy(self, request, pk=None):
        """Allow a user to delete their own profile & account"""
        try:
            profile = Profile.objects.get(pk=pk)

            if profile.user != request.user:
                return Response({'message': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

            user = profile.user
            user.delete()

            return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)
        
    @action(detail=False, methods=['post'], url_path='avatar')
    def upload_avatar(self, request):
        profile = request.user.profile
        file = request.FILES.get('avatar')
        if not file:
            return Response({'avatar': ['File required']}, status=400)
        profile.avatar = file
        profile.save()
        return Response(ProfileSerializer(profile).data, status=201)
