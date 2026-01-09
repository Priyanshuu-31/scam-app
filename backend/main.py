from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="ScamShield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.v1 import scan, report, stats

app.include_router(scan.router, prefix="/api/v1", tags=["Scan"])
app.include_router(report.router, prefix="/api/v1", tags=["Reports"])
app.include_router(stats.router, prefix="/api/v1", tags=["Stats"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ScamShield API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
