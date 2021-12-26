from fastapi import FastAPI
from .routers import pdf
from parse.cameo_selenium_export import cameo_selenium_export, init_driver

init_driver()
app = FastAPI()

app.include_router(pdf.router)

@app.get("/")
async def root():
    """ Test route to check if server is running. """
    return {
        "message": "I am live!",
    }
