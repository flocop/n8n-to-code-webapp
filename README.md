# n8n to Python Code Converter

**Turn your n8n workflows into production-ready Python code in seconds**

## Overview

A web-based SaaS platform that automatically converts n8n visual workflows into clean, deployable Python code. Bridge the gap between rapid prototyping and production deployment.

## Features

- 🔄 Convert n8n JSON workflows to Python code
- 🎯 Support for common n8n nodes (HTTP, Code, If/Switch, etc.)
- 🚀 Generate production-ready async Python code
- 📦 Automatic dependency management (requirements.txt)
- 🌐 Web interface for easy conversion
- 🛠️ CLI tool for local development

## Project Structure

```
n8n-to-code-webapp/
├── backend/              # Python FastAPI backend
│   ├── parser/          # n8n JSON parser
│   ├── generator/       # Python code generator
│   ├── templates/       # Code templates
│   └── api/            # FastAPI endpoints
├── frontend/            # Next.js web interface
├── samples/            # Sample n8n workflows
└── tests/              # Test suite
```

## 🚀 Deploy to Vercel (Easiest!)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/flocop/n8n-to-code-webapp)

**One-click deployment!** Backend + Frontend hosted together on Vercel.

See [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) for detailed instructions.

---

## Quick Start (Local Development)

### Option 1: Docker (Recommended)

```bash
docker-compose up
```

Then open http://localhost:3000 in your browser!

### Option 2: Manual Setup

**1. Install Backend Dependencies**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Test the Installation**

```bash
# From project root
python test_installation.py
```

**3. Try the CLI**

```bash
python -m backend.cli convert samples/simple-http.json -d output/
cd output/
python workflow.py
```

**4. Start the Web Server**

```bash
# From project root
uvicorn backend.api.main:app --reload --port 8000
```

**5. Open the Frontend**

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit http://localhost:3000

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

## Usage

### Web Interface

1. **Export your n8n workflow**
   - Open your workflow in n8n
   - Click menu (⋮) → Download
   - Save the JSON file

2. **Convert**
   - Upload the JSON file to the web interface
   - Click "Convert to Python"
   - Review the generated code

3. **Download and Run**
   - Download the generated `workflow.py`
   - Install dependencies: `pip install -r requirements.txt`
   - Run: `python workflow.py`

### CLI Usage

```bash
# Convert to a single file
python -m backend.cli convert workflow.json -o my_workflow.py

# Convert to a directory (includes requirements.txt and README)
python -m backend.cli convert workflow.json -d output/

# Validate before converting
python -m backend.cli validate workflow.json

# List supported node types
python -m backend.cli supported
```

### API Usage

```bash
# Start the server
uvicorn backend.api.main:app --reload

# API docs available at:
# http://localhost:8000/docs
```

## Supported Nodes

### Currently Supported ✅
- **HTTP Request** - GET, POST, PUT, DELETE requests
- **Code/Function** - Custom JavaScript (needs manual conversion to Python)
- **IF** - Conditional logic and branching
- **Set** - Variable assignment and data manipulation
- **Webhook** - Webhook triggers (converted to function entry points)

### Coming Soon ⏳
- Database nodes (PostgreSQL, MongoDB, MySQL)
- Cloud services (AWS S3, GCP, Azure)
- Popular APIs (Slack, Twilio, SendGrid)
- Data transformation nodes
- Loop and iteration nodes
- Error handling nodes

Run `python -m backend.cli supported` to see the full list.

## Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Jinja2** - Template engine (future use)
- **Black** - Code formatting

### Frontend
- **HTML/CSS/JavaScript** - Simple web interface
- **Tailwind CSS** - Styling
- **Highlight.js** - Syntax highlighting

### Future
- **PostgreSQL** - User accounts, workflow history
- **Redis** - Caching
- **Next.js** - Advanced frontend features

## Examples

Check out the `samples/` directory for example workflows:

- **simple-http.json** - Basic HTTP request
- **http-with-condition.json** - HTTP + conditional logic
- **webhook-workflow.json** - Webhook trigger with processing

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [DEVELOPMENT.md](DEVELOPMENT.md) - Contributor guide
- API Docs: http://localhost:8000/docs (when server is running)

## Development Status

🚧 **MVP Complete - Ready for Testing!**

Current version: **0.1.0**

- ✅ Core parser and generator
- ✅ CLI tool
- ✅ Web API
- ✅ Simple web interface
- ✅ Support for 5+ node types
- ⏳ Advanced node support
- ⏳ User accounts
- ⏳ Workflow library

## Contributing

Contributions are welcome! See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Architecture overview
- How to add new node types
- Development guidelines
- Testing procedures

## Roadmap

### Phase 1 (Current - MVP)
- ✅ Basic node support
- ✅ CLI and web interface
- ✅ Code generation

### Phase 2 (Next)
- [ ] Extended node support (20+ types)
- [ ] Better error handling
- [ ] Unit test generation
- [ ] Environment variable support

### Phase 3 (Future)
- [ ] User authentication
- [ ] Workflow library
- [ ] Advanced customization
- [ ] Code optimization

### Phase 4 (Long-term)
- [ ] SaaS deployment
- [ ] Team collaboration
- [ ] Premium features
- [ ] Enterprise support

## Troubleshooting

**ImportError: No module named 'backend'**
- Make sure you're running from the project root
- Activate your virtual environment

**Port already in use**
- Change the port: `uvicorn backend.api.main:app --port 8001`

**CORS errors**
- Make sure the backend is running on port 8000
- Check the API_URL in `frontend/index.html`

For more help, run: `python test_installation.py`

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built for the n8n community
- Inspired by the need for production-ready code from visual workflows
- Thanks to all contributors!

---

**Made with ❤️ for the n8n community**

Star ⭐ this repo if you find it useful!
