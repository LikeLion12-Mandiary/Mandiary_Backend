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
