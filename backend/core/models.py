# backend/core/models.py

from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model.
    All models in the project must inherit from this.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True