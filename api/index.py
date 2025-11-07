"""
Vercel serverless function entry point for FastAPI
"""
import sys
from pathlib import Path

# Add the project root to Python path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import backend modules
try:
    from backend.api.main import (
        app as backend_app,
        convert_workflow,
        validate_workflow,
        convert_and_download,
        get_supported_nodes,
        health,
        root
    )

    # Create a new FastAPI app for Vercel
    app = FastAPI(
        title="n8n to Python Converter API",
        description="Convert n8n workflows to production-ready Python code",
        version="0.1.0",
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes without /api prefix (Vercel strips it)
    app.get("/")(root)
    app.get("/health")(health)
    app.post("/convert")(convert_workflow)
    app.post("/validate")(validate_workflow)
    app.post("/convert/download")(convert_and_download)
    app.get("/supported-nodes")(get_supported_nodes)

except ImportError as e:
    # Fallback: simple error app
    app = FastAPI()

    @app.get("/")
    async def error_root():
        return {
            "status": "error",
            "message": f"Failed to import backend: {str(e)}",
            "path": str(root_path),
            "sys_path": sys.path[:3]
        }

# Mangum adapter for AWS Lambda/Vercel
handler = Mangum(app)
