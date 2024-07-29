from rest_framework import serializers

from mandalarts.models import Goal, Mandalart, SubGoal

class MandalartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandalart
        fields = '__all__'

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