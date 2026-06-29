"""IntelliPolicy AI — FastAPI application entry point."""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(name)s │ %(message)s")

from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("IntelliPolicy AI starting up...")
    # Only attempt DB init when DATABASE_URL is explicitly provided.
    # Without it the connection attempt to localhost:5432 can hang for
    # minutes and block the healthcheck from ever responding.
    if os.environ.get("DATABASE_URL"):
        try:
            from app.db.setup import init_db
            init_db()
            logging.info("Database initialized")
        except Exception as e:
            logging.warning(f"DB init failed: {e}")
    else:
        logging.info("No DATABASE_URL — running with in-memory store")
    yield
    logging.info("IntelliPolicy AI shutting down")


app = FastAPI(
    title="IntelliPolicy AI",
    description="Agentic AI platform for healthcare policy intelligence, claims validation, and rule automation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
