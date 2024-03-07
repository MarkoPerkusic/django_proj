from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailAuthBackend(object):
    def authenticate(self, request, email=None, password=None):
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
