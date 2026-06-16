from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models import BaseModel
from .managers import CustomUserManager
from django.conf import settings


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseModel):

    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(BaseModel):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ✅ SINGLE CLEAN ADDRESS MODEL

User = settings.AUTH_USER_MODEL

class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    address_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home'),
            ('work', 'Work'),
            ('other', 'Other')
        ],
        default='home'
    )

    country_code = models.CharField(
        max_length=5,
        default='IN',
        help_text="ISO country code (IN, US, GB, etc.)"
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)

    def __str__(self):

        parts = [
            self.full_name,
            self.address_line_1,
            self.city,
            self.state,
        ]

        return ", ".join(
            part for part in parts if part
        )