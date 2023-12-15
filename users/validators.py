from datetime import timezone
from rest_framework.exceptions import ValidationError
from users.models import User, CallbackToken
from config import settings


class InviteCodeValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):

        else_referral_code = value.get(self.field)
        if else_referral_code is not None:
            if self.instance.else_referral_code is not None:
                raise ValidationError('You can activate the invite code only once.')
            else:
                try:
                    else_user = User.objects.get(referral_code=else_referral_code)
                except User.DoesNotExist:
                    raise ValidationError('Incorrect code entered.')
                else:
                    self.instance.else_referral_code = else_user
                    self.instance.save()


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
