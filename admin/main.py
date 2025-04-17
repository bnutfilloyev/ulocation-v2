import os

import uvicorn
# Import app instance
from app import app
from app.admin import admin
from config import initialize_db
from starlette.responses import RedirectResponse
from starlette.routing import Route

# Ensure directories exist
static_dir = "static"  # Create in the current directory

# Create directory structure for static files
os.makedirs(static_dir, exist_ok=True)


# Root redirect to admin
async def homepage(request):
    return RedirectResponse(url="/admin")


# Define core routes
routes = [
    Route("/", endpoint=homepage),
]

# Mount routes
app.routes.extend(routes)

# Mount admin app
admin.mount_to(app)


@app.on_event("startup")
async def startup():
    initialize_db()
    print("Application started successfully")


# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
