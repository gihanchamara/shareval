from fastapi import APIRouter
from backend.app.api.v1.stocks import router as stocks_router
from backend.app.api.v1.options import router as options_router
from backend.app.api.v1.market import router as market_router
from backend.app.api.v1.knowledge import router as knowledge_router

api_v1_router = APIRouter()
api_v1_router.include_router(stocks_router)
api_v1_router.include_router(options_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(knowledge_router)
