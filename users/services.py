import string

from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token


def generate_numeric_token() -> str:

    return get_random_string(length=4, allowed_chars=string.digits)

    # return '1234'


def generate_referral_code() -> str:

    return get_random_string(length=6, allowed_chars=string.digits + string.ascii_lowercase + string.ascii_uppercase)


def send_sms_with_callback_token(user, callback_token, **kwargs) -> None:

    print(f'На телефонный номер {user.phone} отправлен код подтверждения авторизации {callback_token}')


def create_authentication_token(user) -> Token:

    return Token.objects.get_or_create(user=user)[0]
