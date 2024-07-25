from django.db import models

from users.models import User

class Mandalart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(default='만다라트')
    created_at = models.DateField(auto_now_add=True)
    is_achieved = models.BooleanField(default=False)

class Goal(models.Model):
    main_goal = models.CharField(null=True)
    is_achieved = models.BooleanField(default=False)

class SubGoal(models.Model):
    content = models.TextField(null=True)
    image= models.ImageField(upload_to='mandalart')
    is_achieved = models.BooleanField(default=False)