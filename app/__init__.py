from fastapi import FastAPI
from app.api import upload, search

app = FastAPI()

app.include_router(upload.router, prefix="/upload")
app.include_router(search.router, prefix="/search")
