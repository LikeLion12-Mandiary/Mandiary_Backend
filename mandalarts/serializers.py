from rest_framework import serializers

from mandalarts.models import *
from users.serializers import UserSerializer

### MANDALART ###
class MandalartBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandalart
        fields = '__all__'
        
class MandalartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandalart
        fields = ['user','table_name', 'man_title','created_at', 'completed']
        extra_kwargs = {'user': {'required': False}}

class MandalartDetailSerializer(serializers.ModelSerializer):
    goals= serializers.SerializerMethodField()
    class Meta:
        model = Mandalart
        fields = ['user', 'table_name', 'man_title', 'created_at', 'completed', 'goals']
    def get_goals(self, obj):
        goals= Goal.objects.filter(final_goal=obj)
        return GoalSerializer(goals, many=True).data


### GOAL ###
class GoalBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields=['id', 'goal_title', 'completed']

#goal-mandalart
class MandalartGoalSerializer(serializers.ModelSerializer):
    goals = serializers.SerializerMethodField()
    class Meta:
        model = Mandalart
        fields = ['id', 'table_name', 'man_title', 'completed', 'goals']
    def get_goals(self, obj):
        goals= Goal.objects.filter(final_goal=obj)
        return GoalBaseSerializer(goals, many=True).data

class GoalSerializer(serializers.ModelSerializer):
    subgoals = serializers.SerializerMethodField()
    class Meta:
        model = Goal
        fields = ['id', 'goal_title', 'completed', 'subgoals']
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
    badge=BadgeSerializer()
    class Meta:
        model = UserBadge
        fields=['id', 'badge', 'unlocked']

class UserBadgeTitleSerializer(serializers.ModelSerializer):
    badge_title = serializers.SerializerMethodField()
    class Meta:
        model =  UserBadge
        fields= ['badge_title']
    def get_badge_title(self, obj):
        return obj.badge.badge_title if obj.badge else None

class BadgeUnlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeUnlock
        field='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields= ['message']

class GoalAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoalAchievement
        fields='__all__'