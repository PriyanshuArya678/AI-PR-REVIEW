from fastapi import FastAPI

from api.routes import health, webhook


def create_app() -> FastAPI:
    """Build the FastAPI app. Using a factory keeps construction in one place
    and makes the app easy to configure/test later."""
    app = FastAPI(title="AI PR Review")
    app.include_router(health.router)
    app.include_router(webhook.router)
    return app


app = create_app()
