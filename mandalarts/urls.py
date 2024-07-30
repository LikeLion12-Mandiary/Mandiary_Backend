from django.urls import path

from mandalarts.views import *

app_name= 'mandalarts'

urlpatterns = [
    #mandalart
    path('createMandalart/', MandalartCreateView.as_view()),
    path('Mandalart_detail/<int:table_id>/', MandalartDetailView.as_view()),
    path('Mandalart/<int:table_id>/', MandalartUpdateDestroyView.as_view()),

]