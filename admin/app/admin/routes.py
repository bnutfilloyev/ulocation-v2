from starlette.responses import RedirectResponse
from starlette.routing import Route


# Simple redirect route - removed duplicate admin setup code
async def index(request):
    return RedirectResponse(url="/admin")


# Create the routes list
admin_routes = [
    Route("/", endpoint=index),
]
