from typing import Dict, Any
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User, CallbackToken
from users.services import generate_referral_code
from users.validators import InviteCodeValidator, TokenAgeValidator


class LoginSerializer(serializers.ModelSerializer):

    phone = PhoneNumberField(required=True)

    class Meta:
        model = User
        read_only_fields = ("id", )
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
        fields = ['phone', ]


class ProfileSerializer(serializers.ModelSerializer):

    other_referral_code = serializers.CharField(write_only=True)
    entered_referral_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'other_referral_code', 'entered_referral_code']
        validators = [
            InviteCodeValidator(field='else_referal_code')
        ]

    def get_entered_referral_code(self, obj: User) -> list:

        queryset = User.objects.filter(else_referral_code=obj)
        return [ProfileForeignSerializer(q).data for q in queryset]
