# backend/apps/accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel


class User(AbstractUser, BaseModel):
    """
    Custom User model.
    We keep username + email, and add student-related fields later if needed.
    """

    # You can add extra fields here later, for example:
    # phone = models.CharField(max_length=15, blank=True)
    # college = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.username