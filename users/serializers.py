from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password', 'email', 'created_at', 'reset_code']
        extra_kwargs = {
            'password': {'write_only': True},
            'reset_code': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
