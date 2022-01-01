from fastapi import FastAPI
from .routers import pdf, results

app = FastAPI()

app.include_router(pdf.router)
app.include_router(results.router)

@app.get("/")
async def root():
    """ Test route to check if server is running. """
    return {
        "message": "I am live!",
    }
