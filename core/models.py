from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid6 import  uuid7
# Create your models here.
class Profile(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid7)
    name = models.CharField(max_length=255, unique=True)
    gender = models.CharField(max_length=10)
    gender_probability = models.FloatField()
    age = models.IntegerField()
    age_group = models.CharField(max_length=20)
    country_id = models.CharField(max_length=2)
    country_name = models.CharField(max_length=100)
    country_probability = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ADMIN = 'admin'
    ANALYST = 'analyst'
    ROLE_CHOICES = [(ADMIN, 'Admin'), (ANALYST, 'Analyst')]

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False) # [cite: 118]
    github_id = models.CharField(max_length=255, unique=True) # [cite: 118]
    avatar_url = models.URLField(blank=True, null=True) # [cite: 123]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ANALYST) # [cite: 125, 135]
    last_login_at = models.DateTimeField(auto_now=True) # [cite: 131]
    
    # Required for the system to block inactive users [cite: 128, 130]
    is_active = models.BooleanField(default=True)
# Create your models here.
