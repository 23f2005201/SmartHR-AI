from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.models import employee, leave, payroll

app = FastAPI(
    title="SmartHR AI Platform API",
    description="Automated HRMS, Payroll, and Predictive Workforce Analytics Backend Engine",
    version="1.0.0"
)

# Explicitly map the allowed incoming frontend access origins
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Included for fallback safety
]

# Configure cross-origin resource sharing for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Catches browser preflight checks directly and approves them cleanly 
@app.middleware("http")
async def cors_preflight_handler(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    return await call_next(request)

# Mount the consolidated API router matrix
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "online", "system": "SmartHR AI Engine"}