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

#만다라트 title, Goal tiitle 수정
"Mandalart-Goal/<int:table_id>/"
class MandalartGoalUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes= [IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class= MandalartGoalSerializer
    lookup_field='id'
    lookup_url_kwarg='table_id'
    def get_queryset(self):
        return Mandalart.objects.filter(user=self.request.user)

#목표(Goal) 편집
"goal/edit/<int:goal_id>/"
class GoalUpdateView(generics.UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=GoalBaseSerializer
    lookup_field='id'
    lookup_url_kwarg='goal_id'
    def get_queryset(self):
        mandalart_ids = Mandalart.objects.filter(user=self.request.user).values_list('id', flat=True)
        print(mandalart_ids)
        # mandalarts = Mandalart.objects.filter(user=self.request.user)
        return Goal.objects.filter(final_goal__in=mandalart_ids)


##########제거??????????
#목표(Goal) 상세보기 및 편집
"goal/<int:table_id>/<int:goal_id>/"
class GoalView(generics.RetrieveUpdateAPIView): #update 삭제
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
    permission_classes=[IsAuthenticated]
    serializer_class= SubGoalSerializer
    lookup_field= 'id'
    lookup_url_kwarg= 'subgoal_id'
    def get_queryset(self):
        user=self.request.user
        mandalarts = Mandalart.objects.filter(user=user)
        goals = Goal.objects.filter(final_goal__in=mandalarts)
        queryset = SubGoal.objects.filter(goal__in=goals)           #request.user가 작성한 subgoal
        return queryset
    
    def perform_update(self, serializer):
        subgoal = serializer.save()
        update_goal_status(subgoal.goal)

def update_goal_status(goal):
    """GOAL 상태 변경"""
    if not goal.subgoal_set.filter(completed=False).exists():
        user = goal.final_goal.user
        notification, created = Notification.objects.get_or_create(
            user=user,
            message=f"목표를 달성하셨습니다 :) 1개의 뱃지를 잠금해제 해보세요!",
            unlockable_badge_count=1
        )
        if not created:
            notification.unlockable_badge_count += 1
            notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!"
            notification.save()

        if UserBadge.objects.filter(unlocked=False).first():         #잠금해제 할 뱃지 유무
            BadgeUnlock.objects.create(
                user=user,
                is_unlocked=False,
                unlock_notification=notification
            )
        
        goal.completed = True
        goal.save()
        
        update_mandalart_status(goal.final_goal)
    
    else:
        goal.completed = False

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
    permission_classes=[IsAuthenticated, IsAdminUser]
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


#랜덤칭호 표시
"dailyBadge/"
class DailyBadgeTitleView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user=request.user
        daily_badge= set_daily_badge_title(user)
        # serializer = self.get_serializer(daily_badge)
        return Response({'dialy_badge':daily_badge}, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
    

#소감 작성
"goal/<int:goal_id>/achievements/"
class GoalAchieveView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        goal_id = self.kwargs.get('goal_id')
        user = request.user
        try:
            goal = Goal.objects.get(id=goal_id)
        except Goal.DoesNotExist:
            return Response({"detail": "목표가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 목표 달성 기록 조회
        achievements = GoalAchievement.objects.filter(user=user, achieved_goal=goal)
        serializer = GoalAchievementSerializer(achievements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        goal_id = self.kwargs.get('goal_id')
        userbadge_id = request.data.get('userbadge_id')
        feedback = request.data.get('feedback', '')

        try:
            goal = Goal.objects.get(id=goal_id)
            if goal.completed == False:
                return Response({"detail":"목표를 아직 달성하지 않았습니다"},status=status.HTTP_400_BAD_REQUEST)
        except Goal.DoesNotExist:
            return Response({"detail": "목표가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 뱃지 확인 (optinal)
        user_badge = None
        if userbadge_id:
            try:
                user_badge = UserBadge.objects.get(id=userbadge_id)  # UserBadge에서 Badge 추출
                print(user_badge)
            except UserBadge.DoesNotExist:
                return Response({"detail": "뱃지가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 기존 목표 달성 기록 확인
        existing_achievement = GoalAchievement.objects.get(user=user, achieved_goal=goal)

        if existing_achievement:
            if existing_achievement.user_badge:
                return Response({"detail": "이미 뱃지를 선택한 소감이 존재합니다. 기록을 변경할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                existing_achievement.feedback = feedback
                if userbadge_id:
                    existing_achievement.user_badge=user_badge
                existing_achievement.save()
                return Response(GoalAchievementSerializer(existing_achievement).data, status=status.HTTP_200_OK)
        
        # 목표 달성 기록 생성
        serializer = GoalAchievementSerializer(data={
            'user': user.id,
            'achieved_goal': goal.id,
            'user_badge': user_badge.id if user_badge else None,
            'feedback': feedback
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        