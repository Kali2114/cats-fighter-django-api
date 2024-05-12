"""
Database models.
"""
from django.core.exceptions import ValidationError

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Users manager."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """System user."""
    email = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Cat(models.Model):
    """Cat object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    weight = models.FloatField(blank=True)
    color = models.CharField(max_length=50, blank=True)
    dangerous = models.BooleanField(default=True)
    abilities = models.ManyToManyField('Ability')
    fighting_styles = models.ManyToManyField('FightingStyles')

    def __str__(self):
        return self.name


class Ability(models.Model):
    """Abilities for cat objects."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

class FightingStyles(models.Model):
    """Fighting styles for cat objects."""
    CHOICES = (
        ('BX', 'Box'),
        ('KB', 'Kickboxing'),
        ('MT', 'Muay Thai'),
        ('WR', 'Wrestling'),
        ('BJJ', 'Brazilian Jiu-Jitsu')
    )

    name = models.CharField(max_length=50, choices=CHOICES)
    ground_allowed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not any(self.name == choice[0] for choice in self.CHOICES):
            raise ValidationError(f'{self.name} is not a valid choice.')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
