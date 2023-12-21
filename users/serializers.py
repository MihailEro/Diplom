from typing import Dict, Any
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User, CallbackToken
from users.services import generate_referral_code
from users.validators import TokenAgeValidator


class LoginSerializer(serializers.ModelSerializer):

    phone = PhoneNumberField(required=True)

    class Meta:
        model = User
        read_only_fields = ("id",)
        fields = ("id", "phone")

    def create(self, validated_data: dict) -> User:

        instance, _ = User.objects.get_or_create(**validated_data)

        if instance.referral_code is None:
            instance.referral_code = generate_referral_code()
            instance.save()

        token = CallbackToken.objects.create(user=instance)
        token.save()

        return instance


class TokenField(serializers.CharField):

    default_error_messages = {
        'required': 'Invalid Token',
        'invalid': 'Invalid Token',
        'blank': 'Invalid Token',
        'max_length': 'Tokens are {max_length} digits long.',
        'min_length': 'Tokens are {min_length} digits long.'
    }


class VerifyTokenSerializer(serializers.Serializer):

    phone = PhoneNumberField(required=False, max_length=17)
    token = TokenField(min_length=4, max_length=4, validators=[TokenAgeValidator])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

        callback_token = attrs.get('token', None)
        phone = attrs.get('phone', None)
        if callback_token is None or phone is None:
            raise serializers.ValidationError('User authentication data is not provided.')
        try:
            user = User.objects.get(phone=phone)
            CallbackToken.objects.filter(user=user, key=callback_token, is_active=True).first()
            attrs['user'] = user
            user.is_verified = True
            user.save()

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')

        except CallbackToken.DoesNotExist:
            raise serializers.ValidationError('Invalid entered token')
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid user provided.')
        except ValidationError:
            raise serializers.ValidationError('Invalid parameters provided.')
        else:
            return attrs


class TokenResponseSerializer(serializers.Serializer):

    token = serializers.CharField(source='key')
    key = serializers.CharField(write_only=True)


class ProfileForeignSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['phone']


class ProfileSerializer(serializers.ModelSerializer):

    other_referral_code = serializers.CharField(write_only=True)
    entered_referral_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'referral_code', 'other_referral_code', 'else_referral_code', 'entered_referral_code']

    def get_entered_referral_code(self, obj: User) -> list:
        if obj.referral_code:
            entered_referral_code = User.objects.filter(else_referral_code=obj.referral_code)
            return [user.phone for user in entered_referral_code]
        return []

    def is_valid(self, *, raise_exception=False) -> bool:

        else_referral_code = self.initial_data.get('other_referral_code', None)
        if else_referral_code is not None:
            if self.instance.else_referral_code is not None:
                raise serializers.ValidationError('You can activate the invite code only once.')
            else:
                try:
                    else_user = User.objects.get(referral_code=else_referral_code)
                except User.DoesNotExist:
                    raise serializers.ValidationError('Incorrect code entered.')
                else:
                    self.instance.else_referral_code = else_user
                    self.instance.save()

        super().is_valid(raise_exception=raise_exception)
