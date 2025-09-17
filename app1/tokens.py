from django.contrib.auth.tokens import PasswordResetTokenGenerator


import logging
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator

logger = logging.getLogger(__name__)

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

    def check_token(self, user, token):
    
        if not super().check_token(user, token):
            logger.error("Token is invalid.")
            return False

        timestamp = self._num_seconds(self._today())  
        token_creation_time = self._num_seconds(user.last_login or user.date_joined)  

        expiration_time = 300  

        if (timestamp - token_creation_time) > expiration_time:
            logger.error("Token has expired.")
            return False

        return True

    def _num_seconds(self, dt):
        return int(dt.timestamp())

    def _today(self):
        return timezone.now()

account_activation_token = AccountActivationTokenGenerator()
