from django.db import models
from django.utils import timezone

from users.models import User

class Mandalart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=18, default='')
    title = models.CharField(null=True, max_length=18, default='')
    created_at = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.table_name:
            self.table_name= self.generate_table_name()
        super().save(*args, **kwargs)
        if not self.goal_set.exists():
            self.create_goals()

    def create_goals(self):
        for i in range(8):
            goal = Goal.objects.create(final_goal=self)
            for j in range(8):
                subgoal= SubGoal.objects.create(goal=goal)

    def generate_table_name(self):
        count = Mandalart.objects.filter(user=self.user).count()+1
        return f"테이블명{count}"

class Goal(models.Model):
    final_goal = models.ForeignKey(Mandalart, on_delete= models.CASCADE, default='')
    title = models.CharField(null=True, blank=True, max_length=18, default='')
    completed = models.BooleanField(default=False)

class SubGoal(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, default='')
    title = models.CharField(null=True, blank=True, max_length=18, default='')
    image= models.ImageField(upload_to='mandalart/', null=True, blank=True)
    completed = models.BooleanField(default=False)

class Badge(models.Model):
    title = models.CharField(null=False,blank=False, max_length=18)
    image = models.ImageField(upload_to='badge', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    unlocked= models.BooleanField(default=False)
    unlocked_at=models.DateField(null=True, blank=True)
    goal= models.ForeignKey(Goal, on_delete=models.RESTRICT, null=True, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=64)
    is_read = models.BooleanField(default=False)
    unlockable_badge_count= models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

class BadgeUnlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_unlocked = models.BooleanField(default=False)
    unlock_notification = models.ForeignKey(Notification, on_delete=models.CASCADE)

class GoalAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achieved_goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    achievement_date = models.DateField(auto_now_add=True)
    feedback = models.CharField(null=True, blank=True, max_length=18)
    badge = models.ForeignKey(UserBadge, null=True, blank=True, on_delete=models.RESTRICT)

class DailyBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge= models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now=True)