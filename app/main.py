from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import pdf, results

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router)
app.include_router(results.router)

@app.get("/")
async def root():
    """ Test route to check if server is running. """
    return {
        "message": "I am live!",
    }

@app.exception_handler(AssertionError)
def assertions_handler(_, e):
    return PlainTextResponse(str(e), status_code=400)
