"""API v1 Router - Aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    emotions,
    history,
    insights,
    recommendations,
    songs,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    emotions.router, prefix="/emotions", tags=["Emotion Analysis"]
)
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["Recommendations"]
)
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(insights.router, prefix="/insights", tags=["AI Insights"])
api_router.include_router(songs.router, prefix="/songs", tags=["Songs"])
