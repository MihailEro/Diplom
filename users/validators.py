from datetime import timezone
from rest_framework.exceptions import ValidationError
from users.models import User, CallbackToken
from config import settings


class TokenAgeValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        token = value.get(self.field)

        try:
            callback_token = CallbackToken.objects.filter(key=token,
                                                          is_active=True).first()
            seconds = (timezone.now() -
                       callback_token.created_at).total_seconds()
            if seconds <= settings.TOKEN_EXPIRE_TIME:
                return True
            else:
                # Invalidate our token.
                callback_token.is_active = False
                callback_token.save()
                return False

        except CallbackToken.DoesNotExist:
            # No valid token.
            return False
