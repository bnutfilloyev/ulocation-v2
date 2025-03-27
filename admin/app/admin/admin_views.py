from starlette.templating import Jinja2Templates

# Create templates instance
templates = Jinja2Templates(directory="templates")


# Add a global error handler
async def not_found(request, exc):
    """Handle 404 errors with a custom template"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


async def server_error(request, exc):
    """Handle 500 errors with a custom template"""
    return templates.TemplateResponse(
        "500.html", {"request": request, "error": str(exc)}, status_code=500
    )


# Define exception handlers dict for the app
exception_handlers = {404: not_found, 500: server_error}
