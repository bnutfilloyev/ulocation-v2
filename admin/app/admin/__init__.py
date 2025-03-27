from app.utils.auth import MyAuthProvider
from config import Config
from starlette_admin.contrib.mongoengine import Admin

# Create a single admin instance to use throughout the application
admin = Admin(
    title="ULocation Admin",
    base_url=f"{Config.BASE_PATH}/admin",
    route_name="admin",
    auth_provider=MyAuthProvider(login_path="/sign-in", logout_path="/sign-out"),
)


# Function to initialize admin routes
def init_admin():
    # Import here to avoid circular imports
    from app.admin.views import register_admin_views

    register_admin_views(admin)
    return admin
