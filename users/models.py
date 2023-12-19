from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from users.services import generate_numeric_token, generate_referral_code


class MyUserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, phone: str, **extra_fields):

        if not phone:
            raise ValueError('The given phone must be set')

        user = User.objects.get_or_create(phone=phone)

        if user.referral_code is None:
            user.referral_code = generate_referral_code()
            user.save()

        token = CallbackToken.objects.create(user=user)
        token.save()

        return user

    def create_superuser(self, phone, **extra_fields):

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(phone, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user


class User(AbstractUser):

    username = None
    password = None
    phone = models.CharField(
        max_length=12,
        verbose_name='Номер телефона',
        unique=True
    )
    referral_code = models.CharField(max_length=6, null=True, default=None)
    else_referral_code = models.CharField(max_length=6, null=True, default=None)
    is_verified = models.BooleanField(('verified'), default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self) -> str:
        return str(self.phone)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class CallbackToken(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    key = models.CharField(default=generate_numeric_token(), max_length=4)

    class Meta:
        verbose_name = 'Callback Token'
        ordering = ['-id']

    def __str__(self):
        return str(self.key)
