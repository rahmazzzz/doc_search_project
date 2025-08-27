from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import question_routes


logging.basicConfig(level=logging.DEBUG)

from app.routes import auth_routes, file_routes, search_routes

app = FastAPI(
    title="Document Search API",
    version="1.0.0"
)

# CORS middleware (allow all origins — you can restrict it if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(file_routes.router, prefix="/upload", tags=["Upload"])
app.include_router(search_routes.router, prefix="/search", tags=["Search"])
app.include_router(question_routes.router, prefix="/chat", tags=["chat"])
app.include_router(file_routes.router, prefix="/files", tags=["Files"])
# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Search API"}
