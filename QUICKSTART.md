# Quick Start Guide

Get up and running with the n8n to Python Converter in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- A modern web browser

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Test the CLI Tool

Try converting a sample workflow:

```bash
python -m backend.cli convert samples/simple-http.json -d output/
```

This will generate:
- `output/workflow.py` - The Python code
- `output/requirements.txt` - Dependencies
- `output/README.md` - Usage instructions

### 3. Run the Generated Code

```bash
cd output/
pip install -r requirements.txt
python workflow.py
```

## Using the Web Interface

### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn api.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### 2. Open the Frontend

Simply open `frontend/index.html` in your browser. Or use a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Then visit http://localhost:3000

### 3. Convert Your Workflow

1. Export your n8n workflow as JSON:
   - Open your workflow in n8n
   - Click menu (⋮) → Download

2. Upload the JSON file in the web interface

3. Click "Convert to Python"

4. Download or copy the generated code!

## CLI Usage Examples

### Convert and save to a file
```bash
python -m backend.cli convert samples/simple-http.json -o my_workflow.py
```

### Convert and save to a directory (includes requirements.txt and README)
```bash
python -m backend.cli convert samples/http-with-condition.json -d output/my-workflow/
```

### Validate a workflow before converting
```bash
python -m backend.cli validate samples/webhook-workflow.json
```

### List supported node types
```bash
python -m backend.cli supported
```

## API Endpoints

Once the server is running, you can access:

- **API Docs**: http://localhost:8000/docs
- **Convert**: POST http://localhost:8000/api/convert
- **Validate**: POST http://localhost:8000/api/validate
- **Supported Nodes**: GET http://localhost:8000/api/supported-nodes

## Example: Converting via cURL

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "file=@samples/simple-http.json" \
  -o response.json
```

## Troubleshooting

### Module not found error
Make sure you're in the correct directory and the virtual environment is activated:
```bash
cd backend
source venv/bin/activate
```

### Port already in use
Change the port:
```bash
uvicorn api.main:app --reload --port 8001
```

### CORS errors in browser
The backend is configured to allow all origins in development. For production, update the CORS settings in `backend/api/main.py`.

## Next Steps

1. Try converting your own n8n workflows
2. Check the generated code and customize as needed
3. Review the node support status with `python -m backend.cli supported`
4. See the main README.md for more advanced features

## Need Help?

- Check the samples in `samples/` directory
- Review the API documentation at http://localhost:8000/docs
- Look at generated README files for usage instructions
