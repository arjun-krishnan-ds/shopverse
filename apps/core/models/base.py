import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """
    Adds created_at and updated_at fields
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Adds UUID field for public references
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Soft delete instead of permanent delete
    """

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    Combined base model used across the project
    """

    class Meta:
        abstract = True


        