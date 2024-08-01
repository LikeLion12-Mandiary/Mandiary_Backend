from django.urls import path

from mandalarts.views import *

app_name= 'mandalarts'

urlpatterns = [
    #mandalart
    path('createMandalart/', MandalartCreateView.as_view()),
    path('Mandalart_detail/<int:table_id>/', MandalartDetailView.as_view()),
    path('inprogress/', InProgressMandalarListView.as_view()),
    path('complete/', CompleteMandalartListView.as_view()),
    path('Mandalart/<int:table_id>/', MandalartUpdateDestroyView.as_view()),

    #goal, subgoal
    path('goal/<int:table_id>/<int:goal_id>/',GoalView.as_view()),
    path('subgoalUpdate/<int:subgoal_id>/', SubGoalUpdateView.as_view()),
    path('goal/<int:goal_id>/achievements/', GoalAchieveView.as_view()),


    #badge
    path('badge/',BadgeCreateView.as_view()),#관리자
    path('badgeUnlock/<int:badge_id>/', BadgeUnlockView.as_view()),
    path('mybadge/', BadgeView.as_view()), #all badge
    path('UnlockedBadge/', UnlockedBadgeView.as_view()), #

    #badge_title
    path('badgeTitle/', BadgeTitleView.as_view()), #칭호
    path('dailyBadge/', DailyBadgeTitleView.as_view()),

    #알림
    path('notifi/',AlarmView.as_view()),
]