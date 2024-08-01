from rest_framework import serializers

from mandalarts.models import *
from users.serializers import UserSerializer

### MANDALART ###
class MandalartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandalart
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

class MandalartDetailSerializer(serializers.ModelSerializer):
    goals= serializers.SerializerMethodField()
    class Meta:
        model = Mandalart
        fields = ['user', 'table_name', 'title', 'created_at', 'completed', 'goals']
    def get_goals(self, obj):
        goals= Goal.objects.filter(final_goal=obj)
        return GoalSerializer(goals, many=True).data

### GOAL ###
class GoalSerializer(serializers.ModelSerializer):
    subgoals = serializers.SerializerMethodField()
    class Meta:
        model = Goal
        fields = ['id', 'title', 'completed', 'subgoals']
    def get_subgoals(self, obj):
        subgoals = SubGoal.objects.filter(goal=obj)
        return SubGoalSerializer(subgoals, many=True).data

###SUBGOAL###
class SubGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGoal
        # fields= ['id', 'title','image','completed']
        fields = '__all__'

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields='__all__'

class UserBadgeSerializer(serializers.ModelSerializer):
    # badge=BadgeSerializer()
    class Meta:
        model = UserBadge
        # fields=['id', 'badge', 'unlocked', 'unlocked_at']
        fields='__all__'

class BadgeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model= Badge
        fields=['id', 'title']

class UserBadgeTitleSerializer(serializers.ModelSerializer):
    badge = BadgeTitleSerializer()
    class Meta:
        model =  UserBadge
        fields=['badge']

class DailyBadgeSerializer(serializers.ModelSerializer):
    badge_title = BadgeTitleSerializer(source='badge')  # `badge` 필드를 BadgeTitleSerializer로 직렬화

    class Meta:
        model = DailyBadge
        fields = ['badge_title', 'date']

class BadgeUnlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeUnlock
        field='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields= '__all__'

class GoalAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoalAchievement
        fields='__all__'
