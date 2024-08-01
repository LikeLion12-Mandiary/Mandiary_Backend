import random
from django.utils import timezone
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from mandalarts.models import Badge, BadgeUnlock, Goal, Mandalart, Notification
from mandalarts.permissions import IsOwnerOrReadOnly
from mandalarts.serializers import *
from users.models import User

#만다라트 생성
"createMandalart/"
class MandalartCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        user = request.user
        mandalart = Mandalart.objects.create(user=user)
        serializer =MandalartSerializer(mandalart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#만다라트 개별 조회(mandalart,goal,subgoal 모두 표시)
"Mandalart_detail/<int:table_id>/"
class MandalartDetailView(generics.RetrieveAPIView):
    permission_classes=[IsOwnerOrReadOnly]
    serializer_class = MandalartDetailSerializer
    def get_queryset(self):
        return Mandalart.objects.filter(user=self.request.user)
    lookup_field='id'   
    lookup_url_kwarg='table_id'

#진행중인 만다라트
"inprogress/"
class InProgressMandalarListView(generics.ListAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class= MandalartSerializer
    def get_queryset(self):
        return Mandalart.objects.filter(completed=False, user=self.request.user)

#완료한 만다라트
"complete/"
class CompleteMandalartListView(generics.ListAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class= MandalartSerializer
    def get_queryset(self):
        return Mandalart.objects.filter(completed=True, user=self.request.user)

#만다라트 table_name, title 편집
"Mandalart/<int:table_id>/"
class MandalartUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = MandalartSerializer
    lookup_field='id' 
    lookup_url_kwarg='table_id'
    def get_queryset(self):
        return Mandalart.objects.filter(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

#목표(Goal) 상세보기 및 편집
"goal/<int:table_id>/<int:goal_id>/"
class GoalView(generics.RetrieveUpdateAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class = GoalSerializer
    def get_object(self):
        table_id = self.kwargs.get('table_id')
        goal_id = self.kwargs.get('goal_id')
        try:
            mandalart = Mandalart.objects.get(user=self.request.user, id=table_id)
        except Mandalart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            goal = Goal.objects.get(id=goal_id, final_goal=mandalart)
        except Goal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return goal

#세부목표 수정(상태, TITLE, IMAGE)
"subgoalUpdate/<int:subgoal_id>/"
class SubGoalUpdateView(generics.UpdateAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class= SubGoalSerializer
    lookup_field= 'id'
    lookup_url_kwarg= 'subgoal_id'
    def get_queryset(self):
        user=self.request.user
        # subgoals= SubGoal.objects.filter(user__mandalart__goal=self.request.user)

        mandalarts = Mandalart.objects.filter(user=user)
        goals = Goal.objects.filter(final_goal__in=mandalarts)
        queryset = SubGoal.objects.filter(goal__in=goals)

        print("Queryset:", queryset)

        return queryset
    
    def perform_update(self, serializer):
        subgoal = serializer.save()
        update_goal_status(subgoal.goal)

def update_goal_status(goal):
    """GOAL 상태 변경"""
    incompleted_subgoal= goal.subgoal_set.filter(completed=False).exists()
    if incompleted_subgoal:
        goal.completed = False
    else:
        goal.completed = True
        goal.save()

        user = goal.final_goal.user
        notification, created = Notification.objects.get_or_create(
            user=user,
            message=f"목표를 달성하셨습니다 :) 1개의 뱃지를 잠금해제 해보세요!",
            unlockable_badge_count=1
        )
        if not created:
            notification.unlockable_badge_count += 1
            notification.save()
            notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!"
            notification.save()

        available_badge = UserBadge.objects.filter(unlocked=False).first()
        if available_badge:
            BadgeUnlock.objects.get_or_create(
                user=user,
                is_unlocked=False,
                unlock_notification=notification
            )
        update_mandalart_status(goal.final_goal)
    goal.save()

def update_mandalart_status(mandalart):
    """MANDALART 상태 변경"""
    if mandalart.goal_set.filter(completed=False).exists():
        mandalart.completed = False
    else:
        mandalart.completed = True
    mandalart.save()

#관리자(뱃지 생성) 
"badge/"
class BadgeCreateView(generics.CreateAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class=BadgeSerializer
    queryset=Badge.objects.all()

#모든 뱃지
"mybadge/"
class BadgeView(generics.ListAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class=UserBadgeSerializer
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)
    
#뱃지 잠금 해제
"badgeUnlock/<int:badge_id>/"
class BadgeUnlockView(generics.UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializers_class = BadgeUnlockSerializer

    def get_queryset(self):
        return BadgeUnlock.objects.filter(user=self.request.user, is_unlocked=False).order_by('id')
    
    def update(self, request, *args, **kwargs):
        badge_id= kwargs.get('badge_id')
        
        try:
            badge_unlock = self.get_queryset().first()
            if not badge_unlock:
                return Response({"message": "잠금 해제할 BadgeUnlock이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except BadgeUnlock.DoesNotExist:
            return Response({"message": "BadgeUnlock을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 잠금해제 할 Badge
        try:
            user_badge = UserBadge.objects.get(id=badge_id, user=self.request.user) 
            if user_badge.unlocked == True:
                return Response({"message":"잠금 해제가 이미 되어있는 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Badge.DoesNotExist:
            return Response({"message":"존재하지 않는 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # goal = Goal.objects.filter(user__goal=request.user, completed=True).exclude(
        #     id__in=UserBadge.objects.filter(user=request.user, badge=user_badge.badge).values_list('goal_id', flat=True)
        # ).first()

        user=self.request.user

        mandalarts = Mandalart.objects.filter(user=user)

        goals = Goal.objects.filter(final_goal__in=mandalarts, completed=True)
        print(goals)

        # 잠금 해제된 목표를 제외
        excluded_goal_ids = UserBadge.objects.filter(user=user, badge=user_badge.badge).values_list('goal_id', flat=True)
        print(excluded_goal_ids)

        excluded_goal_ids = list(excluded_goal_ids)  # queryset 빈 리스트 처리
        filtered_goals = goals.exclude(id__in=excluded_goal_ids)
        print("filtered_goals:",filtered_goals)
        
        # # 필터링된 Goal 중 제외된 목표를 제외합니다
        # filtered_goals = goals.exclude(id__in=excluded_goal_ids)
        # print(filtered_goals)

        # 첫 번째 필터링된 Goal을 가져옵니다
        goal = filtered_goals.first()

        if not goal:
            return Response({"message": "뱃지를 잠금 해제할 수 있는 완료된 목표가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        badge_unlock.is_unlocked = True
        badge_unlock.save()

        notification = badge_unlock.unlock_notification
        notification.unlockable_badge_count -= 1
        if notification.unlockable_badge_count == 0:
            notification.is_read = True
        notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!"
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


#랜덤칭호 표시
"dailyBadge/"
class DailyBadgeTitleView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=DailyBadgeSerializer

    def get(self, request, *args, **kwargs):
        user=request.user
        print(user)
        daily_badge= set_daily_badge_title(user)
        serializer = self.get_serializer(daily_badge)
        return Response(serializer.data, status=status.HTTP_200_OK)

def set_daily_badge_title(user):
    today = timezone.now().date()
    daily_badge, created = DailyBadge.objects.get_or_create(user=user)

    unlocked_badges = list(UserBadge.objects.filter(user=user, unlocked=True).values_list('badge', flat=True))

    if created or daily_badge.date != today:
        if unlocked_badges:
            badge_id = random.choice(unlocked_badges)
            daily_badge.badge = Badge.objects.get(id=badge_id)
        else:
            daily_badge.badge = None
        daily_badge.date = today
        daily_badge.save()

    return daily_badge

#알람
"notifi/"
class AlarmView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    serializer_class=NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)
