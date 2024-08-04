from django.db import models
from django.utils import timezone

from users.models import User

def mandalart_directory_path(instance, filename):
    # 파일을 'user_<id>/<filename>' 경로에 업로드합니다.
    return f'user_{instance.goal.final_goal.user.id}/mandalart/{filename}'

class Mandalart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=18, default='')
    man_title = models.CharField(null=True, max_length=18, default='')
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
    goal_title = models.CharField(null=True, blank=True, max_length=18, default='')
    completed = models.BooleanField(default=False)

class SubGoal(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, default='')
    subgoal_title = models.CharField(null=True, blank=True, max_length=18, default='')
    image= models.ImageField(upload_to=mandalart_directory_path, null=True, blank=True)
    completed = models.BooleanField(default=False)

class Badge(models.Model):
    badge_title = models.CharField(null=False,blank=False, max_length=18)
    image = models.ImageField(upload_to='badge', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    unlocked= models.BooleanField(default=False)
    unlocked_at=models.DateField(null=True, blank=True)
    goal= models.ForeignKey(Goal, on_delete=models.RESTRICT, null=True, blank=True)  # 중복 잠금해제 제한

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
    user_badge = models.ForeignKey(UserBadge, null=True, blank=True, on_delete=models.RESTRICT)
    class Meta:
        unique_together = ('user', 'achieved_goal')  # 한 목표에 대해 하나의 뱃지만 선택 가능