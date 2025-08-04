from fastapi import FastAPI
from app.api import upload, search
from app.auth import routes as auth_routes

app = FastAPI(
    title="DocSearch",
    description="Upload documents and search answers from them using LLM and vector search",
    version="1.0.0",
)

# Auth routes (register, login)
app.include_router(auth_routes.router, tags=["Auth"])

#  Document handling routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(search.router, prefix="/search", tags=["Search"])
