from django.db import models

from users.models import User

class SubGoal(models.Model):
    content = models.TextField(null=True)
    image= models.ImageField(upload_to='mandalart')
    completed = models.BooleanField(default=False)

class Goal(models.Model):
    main_goal = models.CharField(null=True)
    sub_goal = models.ManyToManyField(SubGoal)
    completed = models.BooleanField(default=False)

class Mandalart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(default='만다라트')
    goal = models.ManyToManyField(Goal)
    created_at = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)