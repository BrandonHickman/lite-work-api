from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from django.contrib.auth.models import User


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        url = serializers.HyperlinkedIdentityField(
            view_name='user',
            lookup_field = 'id'
        )
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')


class Users(ViewSet):

    def retrieve(self, request, pk=None):
        
        try:
            user = User.objects.get(pk=pk)
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)



    def list(self, request):
        
        users = User.objects.all()
        serializer = UserDetailSerializer(
            users, many=True, context={'request': request})
        return Response(serializer.data)