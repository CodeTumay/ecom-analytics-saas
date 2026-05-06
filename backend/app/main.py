from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, auth, dashboard, uploads
from app.core.config import settings
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(uploads.router, tags=["uploads"])
    app.include_router(analysis.router, tags=["analysis"])
    app.include_router(dashboard.router, tags=["dashboard"])

    return app


app = create_app()
