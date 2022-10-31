from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=settings.USERNAME_LENGTH,
        validators=(username_validator,)
    )
    email = models.EmailField(
        'Email пользователя',
        blank=False,
        unique=True,
        max_length=settings.EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.FIRST_NAME_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LAST_NAME_LENGTH,
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.PASSWORD_LENGTH,
        blank=False
    )

    subscribe = models.ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical=False,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

