from django.urls import path
from diarys import views


urlpatterns = [
    path('', views.DiaryCreateAPIView.as_view(), name='DiaryCreate_api_view'),
    path('users_diarys/', views.UserDiarysAPIView.as_view(), name='DiaryList_api_view'),
    path('<int:diary_id>/', views.DiaryRetrieveUpdateDestroyAPIView.as_view(), name='DiaryRetrieveUpdateDestroy_api_view'),
]
