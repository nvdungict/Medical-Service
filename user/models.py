from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        DOCTOR = "DOCTOR", 'Doctor'
        PATIENT = "PATIENT", 'Patient'

    base_role = Role.PATIENT

    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)

    name = models.CharField(max_length=200, null=True, default='Edit your name')
    username = models.CharField(max_length=20, null=True)
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)

    email = models.EmailField(unique=True)

    create_time = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

