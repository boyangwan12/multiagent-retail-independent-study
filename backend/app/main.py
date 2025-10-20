from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fashion Forecast Backend",
    version="0.1.0",
    description="Parameter-Driven Multi-Agent Demand Forecasting & Inventory Allocation System"
)

# CORS configuration (to be refined in later tasks)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fashion Forecast API", "version": "0.1.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
