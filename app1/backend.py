from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailAuthBackend(ModelBackend):
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            print("No username or password provided")
            return None

        try:
            user_model = get_user_model()
            user = user_model.objects.get(email=username)

            if not user.is_active:
                return None  

            if user.check_password(password):
                return user  
            else:
                return None  
        except user_model.DoesNotExist:
            print(f"No user found with email: {username}")
            return None
