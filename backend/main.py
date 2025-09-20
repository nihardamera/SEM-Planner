from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api_endpoints

app = FastAPI(title="SEM Planning Engine API")

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the React frontend (running on a different port)
# to communicate with the FastAPI backend.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://*.railway.app",
    "https://*.vercel.app",
    "https://*.netlify.app",
    "*"  # Allow all origins for deployment (you can restrict this later)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_endpoints.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the SEM Planning Engine API"}