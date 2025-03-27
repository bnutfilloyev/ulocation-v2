from config import Config
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

# Create Starlette application with middleware
middleware = [Middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)]

# Create templates
templates = Jinja2Templates(directory="templates")

# Import error handlers
from app.admin.admin_views import exception_handlers

# Create the app instance
app = Starlette(
    debug=Config.DEBUG, middleware=middleware, exception_handlers=exception_handlers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and initialize admin
from app.admin import admin, init_admin

admin = init_admin()  # Initialize admin and reassign the variable
