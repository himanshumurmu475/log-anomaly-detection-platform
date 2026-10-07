from sqlalchemy import text

from app.database.connection import engine

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers.logs import router as logs_router
from app.routers.analytics import router as analytics_router

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Log Anomaly Detection API is running"}


app.include_router(logs_router)
app.include_router(analytics_router)

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )