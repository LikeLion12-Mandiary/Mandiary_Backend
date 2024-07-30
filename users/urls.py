from django.urls import path
from users import views

urlpatterns = [
    path('',views.UserCreateAPIView.as_view(), name='user_create_api_view'), 
    path('profile/', views.ProfileAPIView.as_view(), name='profile_api_view'),
    path('login/',views.LoginAPIView.as_view(), name='login_api_view'), 
    path('password_reset/', views.EmailConfirmAPIView.as_view(), name='password_reset_request_api_view'),
    path('password_reset_confirm/', views.PasswordChangeAPIView.as_view(), name='password_reset_confirm_api_view'),
]
