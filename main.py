from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import and include routers
from app.api.analyzer import router as analyzer_router
from app.api.batch_analyzer import router as batch_analyzer_router

app.include_router(analyzer_router)
app.include_router(batch_analyzer_router)



# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="USEOAI Backend",
    description="API for technical SEO analysis and semantic evaluation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.analyzer import router as analyzer_router
app.include_router(analyzer_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "USEOAI Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)