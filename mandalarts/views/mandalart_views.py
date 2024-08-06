from rest_framework import generics
from rest_framework.generics import *
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

from mandalarts.permissions import IsOwnerOrReadOnly
from ..models import *
from ..serializers import *
from rest_framework.response import Response
from rest_framework import status

#만다라트 생성
"createMandalart/"
class MandalartCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        user = request.user
        Mandalart.objects.filter(user=user, is_selected=True).update(is_selected=False)
        mandalart = Mandalart.objects.create(user=user, is_selected=True)
        serializer =MandalartBaseSerializer(mandalart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#대표 만다라트 표시
"select/Mandalart/<int:mandalart_id>/"
class SelectMainMandalartView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request, *args, **kwargs):
        mandalart_id = kwargs.get('mandalart_id')
        if not mandalart_id:
            return Response({"detail": "mandalart_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mandalart = Mandalart.objects.get(id=mandalart_id, user=request.user)
        except Mandalart.DoesNotExist:
            return Response({"detail": "Mandalart not found"}, status=status.HTTP_404_NOT_FOUND)

        Mandalart.objects.filter(user=request.user, is_selected=True).update(is_selected=False)
        mandalart.is_selected = True
        mandalart.save()  
        serializer = MandalartBaseSerializer(mandalart)
        return Response(serializer.data, status=status.HTTP_200_OK)

#만다라트 개별 조회(mandalart,goal,subgoal 모두 표시)
"Mandalart_detail/<int:table_id>/"
class MandalartDetailView(generics.RetrieveAPIView):
    permission_classes=[IsOwnerOrReadOnly]
    serializer_class = MandalartDetailSerializer
    def get_queryset(self):
        return Mandalart.objects.filter(user=self.request.user)
    lookup_field='id'   
    lookup_url_kwarg='table_id'

#진행중인 만다라트(selected mandalart 먼저 보여줌)
"inprogress/"
class InProgressMandalarListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MandalartMypageSerializer

    def get_queryset(self):
        return Mandalart.objects.filter(completed=False, user=self.request.user).order_by('-is_selected', 'created_at')

#완료한 만다라트
"complete/"
class CompleteMandalartListView(generics.ListAPIView):
    permission_classes=[IsOwnerOrReadOnly, IsAuthenticated]
    serializer_class= MandalartMypageSerializer
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

#목표(Goal) 상세보기
"goal/<int:table_id>/<int:goal_id>/"
class GoalView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = GoalSerializer
    def get_object(self):
        table_id = self.kwargs.get('table_id')
        goal_id = self.kwargs.get('goal_id')
        try:
            mandalart = Mandalart.objects.get(user=self.request.user, id=table_id)
            goal = get_object_or_404(Goal,id=goal_id, final_goal=mandalart)
            return goal
        except Mandalart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

#세부목표 수정(상태, TITLE, IMAGE)
"subgoalUpdate/<int:subgoal_id>/"
class SubGoalUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubGoalSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'subgoal_id'

    def get_queryset(self):
        user = self.request.user
        mandalarts = Mandalart.objects.filter(user=user)
        goals = Goal.objects.filter(final_goal__in=mandalarts)
        return SubGoal.objects.filter(goal__in=goals)  # request.user가 작성한 subgoal

    def perform_update(self, serializer):
        subgoal = serializer.save()
        goal = subgoal.goal
        
        if goal.completed:
            raise PermissionDenied("이미 달성된 목표의 상태를 변경할 수 없습니다.")
        
        update_goal_status(goal)

def update_goal_status(goal):
    """GOAL 상태 변경"""
    if not goal.subgoal_set.filter(completed=False).exists():
        user = goal.final_goal.user
        notification = Notification.objects.filter(
            user=user,
            message__icontains="목표를 달성하셨습니다 :)",
            unlockable_badge_count__lte=1
        ).first()
        if not notification:
            notification = Notification.objects.create(
                user=user,
                message="목표를 달성하셨습니다 :) 1개의 뱃지를 잠금해제 해보세요!",
                unlockable_badge_count=1
            )
        else:
            notification.unlockable_badge_count += 1
            notification.message = f"목표를 달성하셨습니다 :) {notification.unlockable_badge_count}개의 뱃지를 잠금해제 해보세요!"
            notification.save()
        if UserBadge.objects.filter(user=user, unlocked=False).exists():
            BadgeUnlock.objects.get_or_create(
                user=user,
                unlock_notification=notification,
                defaults={'is_unlocked': False}
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
                user_badge = UserBadge.objects.get(user=user, id=userbadge_id, unlocked=True)  # UserBadge에서 Badge 추출
                print(user_badge)
            except UserBadge.DoesNotExist:
                return Response({"detail": "뱃지가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 기존 목표 달성 기록 확인
        existing_achievement = GoalAchievement.objects.filter(user=user, achieved_goal=goal).first()

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
        