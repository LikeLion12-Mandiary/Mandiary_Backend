from rest_framework import serializers
from .models import Todo
from users.serializers import UserSerializer


class TodoSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Todo
        fields = ['id', 'date', 'time', 'content', 'user']
