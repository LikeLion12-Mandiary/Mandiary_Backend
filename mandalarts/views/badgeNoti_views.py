import random
from rest_framework import generics
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ..models import *
from ..serializers import *
from rest_framework.response import Response
from rest_framework import status



#관리자(뱃지 생성) 
"badge/"
class BadgeCreateView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated, IsAdminUser]
    serializer_class=BadgeSerializer
    queryset=Badge.objects.all()

#모든 뱃지
"mybadge/"
class BadgeView(generics.ListAPIView):
    permission_classes=[ IsAuthenticated]
    serializer_class=UserBadgeSerializer
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)
    
#뱃지 잠금 해제
"badgeUnlock/<int:userbadge_id>/"
class BadgeUnlockView(generics.UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializers_class = BadgeUnlockSerializer

    def get_queryset(self):
        return BadgeUnlock.objects.filter(user=self.request.user, is_unlocked=False).order_by('id')
    
    def update(self, request, *args, **kwargs):
        user=self.request.user
        userbadge_id= kwargs.get('userbadge_id')
        badge_unlock = self.get_queryset().first()
        if not badge_unlock:
            return Response({"message": "목표를 달성해서 뱃지를 잠금해제해보세요"}, status=status.HTTP_404_NOT_FOUND)
        
        # 잠금해제 할 Badge
        try:
            user_badge = UserBadge.objects.get(id=userbadge_id, user=user) 
            if user_badge.unlocked == True:
                return Response({"message":"잠금 해제가 된 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Badge.DoesNotExist:
            return Response({"message":"존재하지 않는 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)

        mandalarts = Mandalart.objects.filter(user=user)
        goals = Goal.objects.filter(final_goal__in=mandalarts, completed=True) #request.user의 달성한 목표 set

        # 잠금 해제된 목표를 제외 (중복 해제 방지)
        excluded_goal_ids = UserBadge.objects.filter(user=user, badge=user_badge.badge).values_list('goal_id', flat=True)
        print(excluded_goal_ids)
        excluded_goal_ids = list(excluded_goal_ids)     # queryset 빈 리스트 처리
        filtered_goals = goals.exclude(id__in=excluded_goal_ids)
        print("filtered_goals:",filtered_goals)

        goal = filtered_goals.first()                   # 가장 먼저 달성된 goal
        if not goal:
            return Response({"message": "뱃지를 잠금 해제할 수 있는 완료된 목표가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        badge_unlock.is_unlocked = True
        badge_unlock.save()

        notification = badge_unlock.unlock_notification
        if notification.unlockable_badge_count == 1:
            notification.unlockable_badge_count -= 1
            notification.is_read = True
        notification.unlockable_badge_count -= 1
        notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!" # msg 업데이트
        notification.save()

        user_badge.unlocked = True
        user_badge.unlocked_at = timezone.now()
        user_badge.goal = goal
        user_badge.save()

        return Response({"message":"뱃지가 잠금해제 되었습니다."}, status=status.HTTP_200_OK)

#잠금 해제한 뱃지 
"UnlockedBadge/"
class UnlockedBadgeView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=UserBadgeSerializer
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user, unlocked=True)


#나의 칭호 
"badgeTitle/"
class BadgeTitleView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=UserBadgeTitleSerializer
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user, unlocked=True)

#모든 칭호(test용)
"AllBadgeTitle/"
class AllBadgeTitleView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=UserBadgeTitleSerializer
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)

#랜덤칭호 표시
"dailyBadge/"
class DailyBadgeTitleView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user=request.user
        daily_badge= set_daily_badge_title(user)
        # serializer = self.get_serializer(daily_badge)
        return Response({'dialy_badge':daily_badge}, status=status.HTTP_200_OK)

def set_daily_badge_title(user):
    unlocked_userbadges = UserBadge.objects.filter(user=user, unlocked=True)
    unlocked_badge_ids = unlocked_userbadges.values_list('badge_id', flat=True)
    unlocked_badges = Badge.objects.filter(id__in=unlocked_badge_ids)
    
    if unlocked_badges.exists():
        random_badge = random.choice(unlocked_badges)
        badge_title = random_badge.badge_title
    else:
        badge_title = "No unlocked badges available"

    return badge_title

#알람
"notifi/"
class NotificationView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)
    
class NotificationStatusView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        has_notifications = Notification.objects.filter(user=user, is_read=False).exists()
        return Response({'has_notifications':has_notifications}, status=status.HTTP_200_OK)
    