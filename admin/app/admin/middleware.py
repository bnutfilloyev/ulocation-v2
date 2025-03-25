from starlette.authentication import AuthenticationBackend, AuthCredentials, BaseUser

class AdminUser(BaseUser):
    def __init__(self, username):
        self.username = username

    @property
    def is_authenticated(self):
        return True

    @property
    def display_name(self):
        return self.username

class SessionAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        """Authenticate a user based on session data"""
        if "username" not in request.session:
            return None
        
        username = request.session["username"]
        return AuthCredentials(["authenticated"]), AdminUser(username)
