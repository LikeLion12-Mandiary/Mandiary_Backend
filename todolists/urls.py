from django.urls import path
from todolists import views

app_name = 'todolists'

urlpatterns = [
    path('', views.TodoListCreateAPIView.as_view(), name='todo_list_create'),
    path('date/<str:selected_date>/', views.TodoByDateAPIView.as_view(), name='todo_by_date'),
    path('delete/<int:todolist_id>/', views.TodoListDestroyAPIView.as_view(), name='todo_delete'),
]