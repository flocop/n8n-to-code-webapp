# Deployment Guide

This guide covers deploying the n8n to Python Converter to production.

## Architecture

- **Frontend**: Static HTML/CSS/JS (deploy to Vercel, Netlify, or any static host)
- **Backend**: Python FastAPI (deploy to Railway, Render, Fly.io, or any Python host)

## 🚀 Quick Deploy (Recommended)

### Step 1: Deploy Backend to Railway

Railway is the easiest way to deploy Python apps.

**Option A: Using Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

**Option B: Using Railway Dashboard**

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `n8n-to-code-webapp` repository
4. Railway will auto-detect the Python app
5. It will automatically run: `pip install -r backend/requirements.txt`
6. Set start command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
7. Deploy!

Your backend will be available at: `https://your-app.railway.app`

### Step 2: Deploy Frontend to Vercel

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd /path/to/n8n-to-code-webapp
vercel
```

**Option B: Using Vercel Dashboard**

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration
5. Click "Deploy"

**Step 3: Configure Frontend to Use Backend**

After deploying, update the backend URL:

1. Edit `frontend/config.js`:
   ```javascript
   window.BACKEND_URL = 'https://your-app.railway.app';
   ```

2. Commit and push:
   ```bash
   git add frontend/config.js
   git commit -m "Update backend URL for production"
   git push
   ```

3. Vercel will automatically redeploy!

---

## Alternative Deployment Options

### Backend Hosting Options

#### Option 1: Render.com (Free tier available)

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: n8n-converter-api
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Click "Create Web Service"

Your API will be at: `https://n8n-converter-api.onrender.com`

#### Option 2: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create `fly.toml` in project root:

```toml
app = "n8n-converter"
primary_region = "lax"

[build]
  dockerfile = "Dockerfile"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
```

4. Update Dockerfile to expose port 8000
5. Deploy: `fly launch` then `fly deploy`

#### Option 3: AWS Lambda (Serverless)

Use Mangum to wrap FastAPI for Lambda:

1. Install: `pip install mangum`
2. Update `backend/api/main.py`:

```python
from mangum import Mangum

# ... existing code ...

handler = Mangum(app)  # Add this at the end
```

3. Use AWS SAM or Serverless Framework to deploy

### Frontend Hosting Options

#### Option 1: Vercel (Recommended)

See Step 2 above.

#### Option 2: Netlify

1. Go to https://netlify.com
2. Drag and drop your `frontend/` folder
3. Or connect GitHub repo and set:
   - **Base directory**: `frontend`
   - **Build command**: (leave empty)
   - **Publish directory**: `.`

#### Option 3: GitHub Pages

```bash
# Create gh-pages branch
git checkout -b gh-pages

# Move frontend files to root
cp frontend/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

Then enable GitHub Pages in repo settings.

#### Option 4: Cloudflare Pages

1. Go to https://pages.cloudflare.com
2. Connect your GitHub repo
3. Set build settings:
   - **Build command**: (none)
   - **Build output directory**: `frontend`

---

## Environment Variables

### Backend Environment Variables

For production deployments, set these in your hosting platform:

```bash
# Optional: Set custom port (most platforms set this automatically)
PORT=8000

# Optional: Configure CORS for your frontend domain
FRONTEND_URL=https://your-app.vercel.app
```

Update `backend/api/main.py` CORS settings if needed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Configuration

Update `frontend/config.js` with your backend URL:

```javascript
window.BACKEND_URL = 'https://your-backend.railway.app';
```

---

## Docker Deployment

### Deploy to Any Container Host

The project includes Docker configuration for easy deployment:

```bash
# Build
docker build -t n8n-converter .

# Run
docker run -p 8000:8000 n8n-converter
```

### Deploy to Docker Hub + Any Platform

```bash
# Build and tag
docker build -t yourusername/n8n-converter:latest .

# Push to Docker Hub
docker push yourusername/n8n-converter:latest
```

Then deploy to:
- AWS ECS
- Google Cloud Run
- Azure Container Apps
- DigitalOcean App Platform

### Using Docker Compose

For a complete setup with both frontend and backend:

```bash
docker-compose up -d
```

---

## Monitoring & Maintenance

### Health Checks

The API includes a health endpoint: `GET /health`

Configure your hosting platform to check this endpoint.

### Logs

- **Railway**: View logs in the dashboard
- **Render**: Real-time logs in the dashboard
- **Fly.io**: `fly logs`

### Scaling

Most platforms offer auto-scaling:
- **Railway**: Auto-scales based on traffic
- **Render**: Configure in dashboard
- **Fly.io**: `fly scale count 3`

---

## Cost Estimates

### Free Tier Options

| Platform | Backend | Frontend | Limits |
|----------|---------|----------|--------|
| Railway | $5/month credit | - | 500 hours/month |
| Render | ✅ Free | ✅ Free | Sleeps after inactivity |
| Vercel | - | ✅ Free | 100GB bandwidth |
| Netlify | - | ✅ Free | 100GB bandwidth |

### Recommended Setup (Free)

- **Backend**: Render.com (Free tier)
- **Frontend**: Vercel (Free tier)
- **Total Cost**: $0/month

### Production Setup ($5-10/month)

- **Backend**: Railway ($5-10/month)
- **Frontend**: Vercel (Free)
- **Total Cost**: $5-10/month

---

## Troubleshooting

### CORS Errors

Update `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    # allow_origins=["https://your-domain.com"],  # For production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Backend Not Starting

Check the start command includes:
```bash
--host 0.0.0.0 --port $PORT
```

### Frontend Can't Connect to Backend

1. Check `frontend/config.js` has correct URL
2. Ensure backend URL doesn't have trailing slash
3. Check CORS settings in backend
4. Verify backend is running: visit `https://your-backend.com/health`

---

## Post-Deployment Checklist

- [ ] Backend is accessible at `/health` endpoint
- [ ] Frontend loads correctly
- [ ] Can upload n8n workflow JSON
- [ ] Conversion works and returns Python code
- [ ] Download functionality works
- [ ] Validation endpoint works
- [ ] Check logs for errors
- [ ] Set up monitoring (optional)
- [ ] Configure custom domain (optional)

---

## Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as shown

### Railway Custom Domain

1. Go to Settings → Domains
2. Click "Add Domain"
3. Follow DNS setup instructions

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Project Issues: https://github.com/yourusername/n8n-to-code-webapp/issues

---

**Deployment made easy! 🚀**

Choose Railway + Vercel for the fastest deployment path.
