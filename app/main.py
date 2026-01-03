from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stations, routes
from app.services.data_store import load_data

app = FastAPI(title="SPUF-314 BMTC Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",]
    ,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_data()
app.include_router(stations.router)
app.include_router(routes.router)
