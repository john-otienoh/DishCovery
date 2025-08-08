from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from datetime import timedelta

class CustomRefreshToken(RefreshToken):
    """Custom refresh token"""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["email"] = user.email  # Add the email to the token payload
        return token


def token_generator(user):
    """get jwt tokens for user"""
    refresh = CustomRefreshToken.for_user(user)
    refresh.set_exp(lifetime=timedelta(days=7))
    access = refresh.access_token
    access.set_exp(lifetime=timedelta(minutes=15))
    return {
        "refresh": str(refresh),
        "access": str(access),
    }


def token_decoder(token):
    """decode jwt token"""
    try:
        # Decode the token
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_data["user_id"]
    except jwt.ExpiredSignatureError:
        # Token has expired
        return {
            "error": "Activation link has expired!",
        }
    except jwt.InvalidTokenError:
        # Token is invalid
        return {
            "error": "Activation link has expired!",
        }
