from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User

from mandalarts.models import Badge, UserBadge

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