from rest_framework import serializers

from mandalarts.models import Badge, BadgeUnlock, Goal, GoalAchievement, Mandalart, Notification, SubGoal

### MANDALART ###
class MandalartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandalart
        fields = '__all__'

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
        fields = ['title', 'completed', 'subgoals']
    def get_subgoals(self, obj):
        subgoals = SubGoal.objects.filter(goal=obj)
        return SubGoalSerializer(subgoals, many=True).data

###SUBGOAL###
class SubGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGoal
        fields= ['id', 'title','image','completed']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields='__all__'

class BadgeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model= Badge
        fields=['id', 'title']

class BadgeUnlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeUnlock
        field='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields= '__all__'
