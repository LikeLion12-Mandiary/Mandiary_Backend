from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status



from mandalarts.models import Badge, BadgeUnlock, Goal, Mandalart, Notification
from mandalarts.serializers import *
from users.models import User

#만다라트 생성
"createMandalart/"
class MandalartCreateView(APIView):
    def post(self, request):
        superuser = User.objects.get(id=1)
        mandalart = Mandalart.objects.create(user=superuser)
        # mandalart.save()
        serializer =MandalartSerializer(mandalart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#만다라트 개별 조회(mandalart,goal,subgoal 모두 표시)
"Mandalart_detail/<int:table_id>/"
class MandalartDetailView(generics.RetrieveAPIView):
    serializer_class = MandalartDetailSerializer
    queryset = Mandalart.objects.all()
    lookup_field='id'   
    lookup_url_kwarg='table_id'

#진행중인 만다라트






#완료한 만다라트



#만다라트 table_name 편집
"Mandalart/<int:table_id>/"
class MandalartUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MandalartSerializer
    queryset = Mandalart.objects.all()
    lookup_field='id'   
    lookup_url_kwarg='table_id'

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
