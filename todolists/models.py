from django.db import models
from users.models import User
from datetime import date


class Todo(models.Model):
    date = models.DateField(default=date.today)
    time = models.TimeField()
    content = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todolists', default=1)