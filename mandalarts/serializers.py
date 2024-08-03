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
    
# class DailyBadgeSerializer(serializers.ModelSerializer):
#     badge_title = serializers.SerializerMethodField()

#     class Meta:
#         model = DailyBadge
#         fields = ['user', 'badge', 'badge_title', 'date']  # Include valid fields

#     def get_badge_title(self, obj):
#         # Ensure obj has 'badge' attribute
#         return obj.user_badge.badge_title if obj.user_badge else None
    
class DailyBadgeSerializer(serializers.Serializer):
    dailybadge=serializers.CharField()


class BadgeUnlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeUnlock
        field='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields= ['message']

# class NotificationStatusSerializer(serializers.Serializer):
#     has_notification = serializers.BooleanField()

class GoalAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoalAchievement
        fields='__all__'

# class UserGoalAchievementSerializer(serializers.ModelSerializer):
#     badge = serializers.PrimaryKeyRelatedField(queryset=Badge.objects.all(), required=False)
#     comment = serializers.CharField(allow_blank=True, required=False)

#     class Meta:
#         model = UserGoalAchievement
#         fields = ['id', 'user', 'achieved_goal', 'badge', 'comment']
#         extra_kwargs = {
#             'user': {'read_only': True},  # 사용자는 요청에 의해 설정되지 않음
#             'achieved_goal': {'read_only': True},  # 목표는 요청에 의해 설정되지 않음
#         }