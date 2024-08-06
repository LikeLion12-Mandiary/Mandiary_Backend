from django.db.models.signals import post_save
from django.dispatch import receiver
from config import settings
from users.models import User

from mandalarts.models import Badge, Mandalart, UserBadge

@receiver(post_save, sender=Badge)
def assign_badge_to_all_users(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            UserBadge.objects.create(user=user, badge=instance)

@receiver(post_save, sender=User)
def assign_badges_to_new_user(sender, instance, created, **kwargs):
    if created:
        badges = Badge.objects.all()
        for badge in badges:
            UserBadge.objects.create(user=instance, badge=badge)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_mandalart_for_new_user(sender, instance, created, **kwargs):
    if created:
        # 새로운 사용자가 생성된 경우에만 만다라트 생성
        Mandalart.objects.create(user=instance, is_selected=True, table_name="테이블명1", man_title="")