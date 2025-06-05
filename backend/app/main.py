"""FastAPI application entrypoint."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import RUN_HOST, RUN_PORT
from app.api import auth, users, avatar, chat

app = FastAPI(title="Mail Chat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve avatar files
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(avatar.router)
app.include_router(chat.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=RUN_HOST, port=RUN_PORT, reload=True)
