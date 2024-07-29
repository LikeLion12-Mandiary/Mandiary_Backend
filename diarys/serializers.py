from rest_framework import serializers
from diarys.models import Diary
from users.serializers import UserSerializer

class DiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Diary
        fields = ['id', 'content','image', 'created_at', 'updated_at', 'user']
