"""FastAPI application for n8n to Python converter"""

import io
import json
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.parser import WorkflowParser
from backend.generator import PythonCodeGenerator


# Create FastAPI app
app = FastAPI(
    title="n8n to Python Converter API",
    description="Convert n8n workflows to production-ready Python code",
    version="0.1.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ConversionResponse(BaseModel):
    """Response for code conversion"""
    success: bool
    workflow_name: str
    python_code: str
    requirements: str
    readme: str
    nodes_count: int
    supported_nodes: int
    unsupported_nodes: list[str]


class ValidationResponse(BaseModel):
    """Response for workflow validation"""
    success: bool
    workflow_name: str
    nodes_count: int
    is_valid: bool
    errors: list[str]
    execution_order: list[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/api/convert", response_model=ConversionResponse)
async def convert_workflow(file: UploadFile = File(...)):
    """
    Convert an n8n workflow JSON file to Python code.

    Args:
        file: Uploaded n8n workflow JSON file

    Returns:
        ConversionResponse with generated code and metadata
    """
    try:
        # Read and parse the uploaded file
        contents = await file.read()
        workflow_data = json.loads(contents.decode("utf-8"))

        # Parse workflow
        workflow = WorkflowParser.parse_dict(workflow_data)

        # Generate code
        generator = PythonCodeGenerator(workflow)
        python_code = generator.generate()
        requirements = generator.generate_requirements()
        readme = generator.generate_readme()

        # Determine supported/unsupported nodes
        from backend.generator import NodeGeneratorRegistry

        unsupported = []
        supported_count = 0

        for node in workflow.nodes:
            generator_obj = NodeGeneratorRegistry.get_generator(node.type)
            if generator_obj:
                supported_count += 1
            else:
                unsupported.append(f"{node.name} ({node.type})")

        return ConversionResponse(
            success=True,
            workflow_name=workflow.name,
            python_code=python_code,
            requirements=requirements,
            readme=readme,
            nodes_count=len(workflow.nodes),
            supported_nodes=supported_count,
            unsupported_nodes=unsupported,
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_workflow(file: UploadFile = File(...)):
    """
    Validate an n8n workflow JSON file.

    Args:
        file: Uploaded n8n workflow JSON file

    Returns:
        ValidationResponse with validation results
    """
    try:
        # Read and parse the uploaded file
        contents = await file.read()
        workflow_data = json.loads(contents.decode("utf-8"))

        # Parse workflow
        workflow = WorkflowParser.parse_dict(workflow_data)

        # Validate
        is_valid, errors = WorkflowParser.validate_workflow(workflow)

        # Get execution order
        execution_order = workflow.get_execution_order()

        return ValidationResponse(
            success=True,
            workflow_name=workflow.name,
            nodes_count=len(workflow.nodes),
            is_valid=is_valid,
            errors=errors,
            execution_order=execution_order,
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.post("/api/convert/download")
async def convert_and_download(file: UploadFile = File(...)):
    """
    Convert workflow and download as Python file.

    Args:
        file: Uploaded n8n workflow JSON file

    Returns:
        Python file as download
    """
    try:
        # Read and parse the uploaded file
        contents = await file.read()
        workflow_data = json.loads(contents.decode("utf-8"))

        # Parse workflow
        workflow = WorkflowParser.parse_dict(workflow_data)

        # Generate code
        generator = PythonCodeGenerator(workflow)
        python_code = generator.generate()

        # Create file-like object
        file_like = io.BytesIO(python_code.encode("utf-8"))

        # Return as downloadable file
        return StreamingResponse(
            file_like,
            media_type="text/x-python",
            headers={
                "Content-Disposition": f"attachment; filename=workflow.py"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.get("/api/supported-nodes")
async def get_supported_nodes():
    """
    Get list of supported node types.

    Returns:
        List of supported n8n node types
    """
    from backend.generator import NodeGeneratorRegistry

    node_types = NodeGeneratorRegistry.get_supported_types()

    # Categorize nodes
    categories = {
        "triggers": [],
        "actions": [],
        "logic": [],
        "core": [],
    }

    for node_type in sorted(node_types):
        if "trigger" in node_type.lower() or "webhook" in node_type.lower():
            categories["triggers"].append(node_type)
        elif "if" in node_type.lower() or "switch" in node_type.lower():
            categories["logic"].append(node_type)
        elif "http" in node_type.lower() or "request" in node_type.lower():
            categories["actions"].append(node_type)
        else:
            categories["core"].append(node_type)

    return {
        "total": len(node_types),
        "categories": categories,
        "all_types": node_types,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
