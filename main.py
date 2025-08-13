from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Scraper"}
