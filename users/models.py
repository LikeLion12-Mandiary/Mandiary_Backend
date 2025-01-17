from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']