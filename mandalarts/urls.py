from django.urls import path

from mandalarts.views import *

app_name= 'mandalarts'

urlpatterns = [
    path('createMandalart/', MandalartCreateView.as_view()),
    path('retrieveUpdateDestroyMandalart/<int:table_id>/', MandalartRetrieveUpdateDestroyView.as_view()),
]