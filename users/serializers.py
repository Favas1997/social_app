
from rest_framework import serializers
from users import models


class SignInSerializer(serializers.Serializer): 
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1, max_length=50, required=True)

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(min_length=100,max_length=300,required=True)


class SignUpSerializer(serializers.Serializer): 
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1, max_length=50, required=True)
    name = serializers.CharField(min_length=1, max_length=50, required=True)


class UserModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name')
    class Meta:
        model=models.User
        fields = ['id','email', 'name']


class FriendRequestSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField(required=True)


class FriendRequestAcknSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(required=True)
    action = serializers.CharField(min_length=3, max_length=10, required=True)


class FriendRequestModelSerializer(serializers.Serializer):
    name = serializers.CharField(source='user2.first_name')
    email = serializers.CharField(source='user2.email')
    class Meta:
        model=models.User
        fields = ['id','email', 'name']