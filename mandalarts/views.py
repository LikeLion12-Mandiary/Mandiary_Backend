from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status



from mandalarts.models import Goal, Mandalart
from mandalarts.serializers import *
from users.models import User

class MandalartCreateView(APIView):
    def post(self, request):
        superuser = User.objects.get(id=1)
        mandalart = Mandalart.objects.create(user=superuser)
        # mandalart.save()
        serializer =MandalartSerializer(mandalart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MandalartRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MandalartSerializer
    queryset = Mandalart.objects.all()
    lookup_field='id'   
    lookup_url_kwarg='table_id'
