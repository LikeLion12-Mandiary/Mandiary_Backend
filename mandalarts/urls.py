from django.urls import path

from mandalarts.views.mandalart_views  import *
from mandalarts.views.badgeNoti_views import *

app_name= 'mandalarts'

urlpatterns = [
    #mandalart
    path('createMandalart/', MandalartCreateView.as_view()),
    path('select/Mandalart/<int:mandalart_id>/', SelectMainMandalartView.as_view()),
    path('Mandalart_detail/<int:table_id>/', MandalartDetailView.as_view()),
    path('inprogress/', InProgressMandalarListView.as_view()),
    path('complete/', CompleteMandalartListView.as_view()),
    path('Mandalart/<int:table_id>/', MandalartUpdateDestroyView.as_view()),
    path('Mandalart-Goal/<int:table_id>/', MandalartGoalUpdateView.as_view()),

    #goal, subgoal
    path('goal/<int:table_id>/<int:goal_id>/',GoalView.as_view()),
    path('subgoalUpdate/<int:subgoal_id>/', SubGoalUpdateView.as_view()),
    path('goal/<int:goal_id>/achievements/', GoalAchieveView.as_view()),
    path('goal/edit/<int:goal_id>/',GoalUpdateView.as_view()),


    #badge
    path('badge/',BadgeCreateView.as_view()),#관리자
    path('badgeUnlock/<int:userbadge_id>/', BadgeUnlockView.as_view()),
    path('mybadge/', BadgeView.as_view()), #all badge
    path('UnlockedBadge/', UnlockedBadgeView.as_view()), #

    #badge_title
    path('AllBadgeTitle/', AllBadgeTitleView.as_view()), #모든 칭호 test
    path('badgeTitle/', BadgeTitleView.as_view()), #칭호
    path('dailyBadge/', DailyBadgeTitleView.as_view()),

    #알림
    path('notifi/',NotificationView.as_view()),
    path('notifi/status/',NotificationStatusView.as_view()),
]