from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseServerError
from workoutapi.models.profile import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_image_url', 'created_at'
        ]

class ProfileViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            profile = Profile.objects.get(pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Allow a user to update their own profile"""
        try:
            profile = Profile.objects.get(pk=pk)

            # Only the owner can update
            if profile.user != request.user:
                return Response({'message': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

            # Update editable fields
            profile.bio = request.data.get('bio', profile.bio)
            profile.profile_image_url = request.data.get('profile_image_url', profile.profile_image_url)
            profile.save()

            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Allow a user to delete their own profile & account"""
        try:
            profile = Profile.objects.get(pk=pk)

            # Only the owner can delete
            if profile.user != request.user:
                return Response({'message': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

            # Delete the associated User (will also cascade delete the Profile)
            user = profile.user
            user.delete()

            return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)
