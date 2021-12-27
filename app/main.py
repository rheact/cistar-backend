from fastapi import FastAPI

from models import SDSExtraction
from .routers import pdf
from cameo.crawler import cameo_selenium_export, init_driver

init_driver()
app = FastAPI()

app.include_router(pdf.router)

@app.get("/")
async def root():
    """ Test route to check if server is running. """
    return {
        "message": "I am live!",
    }
