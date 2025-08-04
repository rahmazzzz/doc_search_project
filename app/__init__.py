from fastapi import FastAPI
from app.routers import upload, search

app = FastAPI()

app.include_router(upload.router, prefix="/upload")
app.include_router(search.router, prefix="/search")
