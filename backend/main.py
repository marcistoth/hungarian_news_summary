import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from endpoints import summaries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)



def create_app() -> FastAPI:
    logger.info("Starting application initialization...")
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(settings, "CORS_ORIGINS", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(summaries.router)
    
    return app

app = create_app()



if __name__ == "__main__":
    import uvicorn
    #uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)