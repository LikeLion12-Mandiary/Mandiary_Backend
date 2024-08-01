from rest_framework import serializers
from diarys.models import Diary
from users.serializers import UserSerializer

class DiarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Diary
        fields = "__all__"
