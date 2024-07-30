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
        subgoals = SubGoal.objects.filter(goal_id=obj.id)
        return SubGoalSerializer(subgoals, many=True).data

class SubGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubGoal
        fields= '__all__'