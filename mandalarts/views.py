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
"goal/<int:table_id>/<int:goal_index>/"
class GoalView(generics.RetrieveUpdateAPIView):
    serializer_class = GoalSerializer
    def get_object(self):
        table_id= self.kwargs.get('table_id')
        goal_index= self.kwargs.get('goal_index') #index 범위(0~7)
        try:
            mandalart= Mandalart.objects.get(id=table_id)
        except Mandalart.DoesNotExist:
            Response(status=status.HTTP_404_NOT_FOUND)
        
        goals = Goal.objects.filter(final_goal=mandalart).order_by('id')
        
        if goal_index >= len(goals) or goal_index < 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return goals[goal_index]

#세부목표 수정(상태, TITLE, IMAGE)
"subgoalUpdate/<int:subgoal_id>/"
class SubGoalUpdateView(generics.UpdateAPIView):
    serializer_class= SubGoalSerializer
    queryset= SubGoal.objects.all()
    lookup_field= 'id'
    lookup_url_kwarg= 'subgoal_id'

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

        ######user 변경 필요#######
        superuser=User.objects.get(id=1)
        # user = goal.final_goal.user
        ##########################

        notification, created = Notification.objects.get_or_create(
            user=superuser,
            # user=user,
            # defaults={'message': '목표를 달성하셨습니다 :) 1개의 뱃지를 잠금해제 해보세요!', 'unlockable_badge_count': 1}
            message=f"목표를 달성하셨습니다 :) 1개의 뱃지를 잠금해제 해보세요!",
            unlockable_badge_count=1
        )
        if not created:
            notification.unlockable_badge_count += 1
            notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!"
            notification.save()

        available_badge = Badge.objects.filter(unlocked=False).first()
        if available_badge:
            BadgeUnlock.objects.create(
                user=superuser,
                # user=user,
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
    serializer_class=BadgeSerializer
    queryset=Badge.objects.all()

#모든 뱃지
"mybadge/"
class BadgeView(generics.ListAPIView):
    serializer_class=BadgeSerializer
    queryset=Badge.objects.all()

#뱃지 잠금 해제
"badgeUnlock/<int:badge_unlock_id>/<int:badge_id>/"
class BadgeUnlockView(generics.UpdateAPIView):
    serializers_class = BadgeUnlockSerializer
    queryset=BadgeUnlock.objects.all()
    
    def update(self, request, *args, **kwargs):
        badge_unlock_id= kwargs.get('badge_unlock_id')
        badge_id= kwargs.get('badge_id')
        
        #BadgeUnlock
        try:
            badge_unlock= BadgeUnlock.objects.get(id=badge_unlock_id, is_unlocked=False) #나중에 user=request.user 추가
        except BadgeUnlock.DoesNotExist:
            return Response({"message":"올바르지 않는 Badge Unlock id입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 잠금해제 할 Badge
        try:
            badge = Badge.objects.get(id=badge_id) 
            if badge.unlocked == True:
                return Response({"message":"잠금 해제가 이미 되어있는 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Badge.DoesNotExist:
            return Response({"message":"존재하지 않는 뱃지입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        badge_unlock.is_unlocked = True
        badge_unlock.save()

        notification = badge_unlock.unlock_notification
        notification.unlockable_badge_count -= 1
        if notification.unlockable_badge_count == 0:
            notification.is_read = True
        notification.save()

        badge.unlocked = True
        badge.save()

        return Response({"message":"뱃지가 잠금해제 되었습니다."}, status=status.HTTP_200_OK)

#잠금 해제한 뱃지
"UnlockedBadge/"
class UnlockedBadgeView(generics.ListAPIView):
    serializer_class=BadgeSerializer
    queryset=Badge.objects.filter(unlocked=True)


#나의 칭호
"badgeTitle/"
class BadgeTitleView(generics.ListAPIView):
    serializer_class=BadgeTitleSerializer
    queryset=Badge.objects.filter(unlocked=True)


#랜덤칭호 표시







#알람
"notifi/"
class AlarmView(generics.ListAPIView):
    serializer_class=NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(user=User.objects.get(id=1), is_read=False) ##request.user로 변경 필요


#소감 작성
"goalAchieve/<int:goal_id>/"
class GoalAchieveView(generics.ListCreateAPIView):
    serializer_class=GoalAchievementSerializer

    def perform_create(self, serializer):
        # user = self.request.user
        user = User.objects.get(id=1)
        goal_id = self.kwargs.get('goal_id') 
        badge_id = self.request.data.get('badge_id') 
        feedback = self.request.data.get('feedback', '')  

        try:
            goal = Goal.objects.get(id=goal_id)
        except Goal.DoesNotExist:
            raise serializers.ValidationError("목표가 존재하지 않습니다.")

        if badge_id:
            try:
                badge = Badge.objects.get(id=badge_id)
            except Badge.DoesNotExist:
                raise serializers.ValidationError("뱃지가 존재하지 않습니다.")
        else:
            badge = None

        # 기존 목표 달성 기록이 있는지 확인하고, 있으면 업데이트
        user_goal_achievement, created = GoalAchievement.objects.update_or_create(
            user=user,
            achieved_goal=goal,
            defaults={'badge': badge, 'feedback': feedback}
        )
        
        return user_goal_achievement