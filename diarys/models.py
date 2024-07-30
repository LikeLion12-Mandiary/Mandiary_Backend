from django.db import models
from users.models import User

def diary_directory_path(instance, filename):
    # 파일을 'user_<id>/<filename>' 경로에 업로드합니다.
    return f'user_{instance.user.id}/diary/{filename}'

class Diary(models.Model):
    content = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to=diary_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diarys')