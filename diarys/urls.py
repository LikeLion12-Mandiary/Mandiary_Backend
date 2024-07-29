from django.urls import path
from diarys import views

app_name = 'diarys'

urlpatterns = [
    path('', views.DiaryListCreateAPIView.as_view(), name='DiaryListCreate'),
    path('<int:diary_id>/', views.DiaryRetrieveUpdateDestroyAPIView.as_view(), name='DiaryRetrieveUpdateDestroy'),
]
