from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging


app = FastAPI(
    title = "Paper Submission Recommendation System",
    version = "1.0.0",
    docs_url = "/api/docs",
    redoc_url = "/api/redoc",
    openapi_url="/api/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )


#Health check endpoint
@app.get("/health", tags = ["Health"])
async def health_check():
    """ Check if API is running """
    return {
        "status": "healthy",
        "service": "paper-submission-rcm-system-api",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """ API root endpoint """
    return {
        "message": "Paper Submission RCM System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
