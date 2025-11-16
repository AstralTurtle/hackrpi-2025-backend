import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.config import LOGGING_CONFIG


from routers import game, health

app = FastAPI()
app.include_router(game.router)
app.include_router(health.router)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=LOGGING_CONFIG,
    )
