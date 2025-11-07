# Development Guide

Guide for developers who want to contribute or extend the n8n to Python Converter.

## Project Structure

```
n8n-to-code-webapp/
├── backend/                    # Python backend
│   ├── parser/                # n8n workflow parser
│   │   ├── models.py         # Pydantic models for n8n structure
│   │   └── parser.py         # JSON parsing logic
│   ├── generator/            # Python code generator
│   │   ├── generator.py      # Main generator orchestration
│   │   └── node_generators.py # Node-specific generators
│   ├── api/                  # FastAPI web service
│   │   └── main.py          # API endpoints
│   ├── cli.py               # Command-line interface
│   └── requirements.txt     # Python dependencies
├── frontend/                 # Web interface
│   └── index.html           # Single-page application
├── samples/                  # Sample n8n workflows
│   ├── simple-http.json
│   ├── http-with-condition.json
│   └── webhook-workflow.json
└── tests/                    # Test suite (future)
```

## Architecture

### 1. Parser Layer (`backend/parser/`)

**Purpose**: Parse and validate n8n workflow JSON files.

**Key Components**:
- `models.py`: Pydantic models that define the structure of n8n workflows
  - `N8nWorkflow`: Root workflow model
  - `N8nNode`: Individual node model
  - `N8nConnection`: Connection between nodes
- `parser.py`: Parser logic
  - `WorkflowParser.parse_file()`: Load from file
  - `WorkflowParser.parse_string()`: Load from JSON string
  - `WorkflowParser.validate_workflow()`: Validation logic

**Key Features**:
- Flexible schema (uses `extra = "allow"`)
- Topological sort for execution order
- Connection graph traversal
- Validation of node references

### 2. Generator Layer (`backend/generator/`)

**Purpose**: Generate Python code from parsed workflows.

**Key Components**:
- `node_generators.py`: Individual node type generators
  - `NodeGenerator`: Abstract base class
  - `HttpRequestGenerator`: HTTP request nodes
  - `CodeNodeGenerator`: Code/Function nodes
  - `IfNodeGenerator`: Conditional logic
  - `SetNodeGenerator`: Variable assignment
  - `WebhookTriggerGenerator`: Webhook triggers
  - `NodeGeneratorRegistry`: Central registry

- `generator.py`: Main orchestration
  - `PythonCodeGenerator`: Coordinates code generation
  - Imports management
  - Dependencies tracking
  - Code assembly

**Code Generation Flow**:
1. Get execution order from workflow
2. For each node, find appropriate generator
3. Generate node function
4. Track imports and dependencies
5. Generate main execution function
6. Assemble complete code

### 3. API Layer (`backend/api/`)

**Purpose**: Expose REST API for web interface.

**Endpoints**:
- `POST /api/convert`: Convert workflow to Python
- `POST /api/validate`: Validate workflow
- `POST /api/convert/download`: Download Python file
- `GET /api/supported-nodes`: List supported nodes

**Response Models**:
- `ConversionResponse`: Conversion results
- `ValidationResponse`: Validation results
- `HealthResponse`: Health check

### 4. CLI Layer (`backend/cli.py`)

**Purpose**: Command-line interface for local usage.

**Commands**:
- `convert`: Convert workflow to Python
- `validate`: Validate workflow structure
- `supported`: List supported node types

### 5. Frontend (`frontend/`)

**Purpose**: Web-based user interface.

**Features**:
- Drag-and-drop file upload
- Real-time conversion
- Syntax-highlighted code preview
- Download functionality
- Validation checks

## Adding Support for New Node Types

To add support for a new n8n node type:

### 1. Create a Node Generator

Add a new class in `backend/generator/node_generators.py`:

```python
class YourNodeGenerator(NodeGenerator):
    """Generator for YourNode type"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters

        # Extract parameters
        your_param = params.get("yourParam", "default")

        # Generate code
        code = f'''async def {self._safe_name(node.name)}({input_var}):
    """Your Node: {node.name}"""
    # Your implementation here
    result = do_something({input_var}, "{your_param}")
    return result
'''

        return {
            "code": code,
            "imports": ["import your_module"],
            "dependencies": ["your-package>=1.0.0"],
        }
```

### 2. Register the Generator

At the bottom of `node_generators.py`:

```python
NodeGeneratorRegistry.register("n8n-nodes-base.yourNode", YourNodeGenerator())
```

### 3. Test

Create a sample workflow in `samples/` and test:

```bash
python -m backend.cli convert samples/your-test.json -d output/
```

## Testing

### Run Installation Tests

```bash
python test_installation.py
```

### Manual Testing

1. **CLI Testing**:
```bash
python -m backend.cli convert samples/simple-http.json -d output/
cd output/
python workflow.py
```

2. **API Testing**:
```bash
# Start server
uvicorn backend.api.main:app --reload

# In another terminal
curl -X POST http://localhost:8000/api/convert \
  -F "file=@samples/simple-http.json"
```

3. **Frontend Testing**:
- Open `frontend/index.html` in browser
- Upload a sample workflow
- Verify conversion

## Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use Black (`black backend/`)
- **Type Hints**: Use Python type hints where possible
- **Docstrings**: Document all public functions

## Common Development Tasks

### Add a New API Endpoint

Edit `backend/api/main.py`:

```python
@app.post("/api/your-endpoint")
async def your_endpoint(file: UploadFile = File(...)):
    # Your implementation
    return {"result": "success"}
```

### Modify Generated Code Format

Edit `backend/generator/generator.py`:
- `_generate_main_function()`: Change main workflow structure
- `_assemble_code()`: Change overall code structure

### Change CLI Behavior

Edit `backend/cli.py`:

```python
@cli.command()
@click.argument("...")
def your_command(...):
    # Your implementation
    pass
```

## Debugging Tips

### Enable Verbose Logging

Add to your code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Parsed Workflow

```python
from backend.parser import WorkflowParser

workflow = WorkflowParser.parse_file("samples/simple-http.json")
print(workflow.model_dump_json(indent=2))
```

### Test Node Generator

```python
from backend.generator import NodeGeneratorRegistry
from backend.parser.models import N8nNode

generator = NodeGeneratorRegistry.get_generator("n8n-nodes-base.httpRequest")
node = N8nNode(name="Test", type="n8n-nodes-base.httpRequest", parameters={})
result = generator.generate(node)
print(result["code"])
```

## Performance Considerations

- Parser uses Pydantic for fast validation
- Generator uses string concatenation (fast for small files)
- For large workflows, consider streaming responses

## Security Considerations

- Validate all uploaded files
- Sanitize node names for Python variables
- Don't execute generated code automatically
- In production, use proper CORS settings

## Future Enhancements

Potential areas for contribution:

1. **More Node Support**
   - Database nodes (PostgreSQL, MongoDB, MySQL)
   - Cloud services (AWS S3, GCP)
   - Popular integrations (Slack, Twilio, Email)

2. **Code Quality**
   - Generate unit tests
   - Add error handling to generated code
   - Support for environment variables

3. **Advanced Features**
   - Sub-workflow support
   - Loop nodes
   - Merge/split data flows
   - Custom credential handling

4. **Web Interface**
   - Live code preview
   - Workflow visualization
   - Code editing before download
   - User accounts and history

5. **CLI Enhancements**
   - Batch conversion
   - Watch mode
   - Configuration files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
