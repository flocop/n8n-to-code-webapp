# Deploy to Vercel - Complete Guide

This project is now configured to deploy entirely to Vercel (both backend and frontend)!

## 🚀 One-Click Deploy

The easiest way to deploy:

### Option 1: Vercel Dashboard (Recommended)

1. **Go to** [vercel.com](https://vercel.com)
2. **Sign in** with GitHub
3. **Click** "Add New" → "Project"
4. **Import** your `n8n-to-code-webapp` repository
5. **Click** "Deploy" (no configuration needed!)

That's it! Vercel will:
- Build the Python backend as serverless functions
- Serve the static frontend
- Give you a URL like `https://your-app.vercel.app`

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to your project
cd n8n-to-code-webapp

# Deploy
vercel

# Follow the prompts:
# - Link to existing project? No
# - Project name: n8n-converter (or your choice)
# - Directory: ./ (just press Enter)
# - Want to override settings? No

# For production deployment
vercel --prod
```

## 📁 Project Structure for Vercel

```
n8n-to-code-webapp/
├── api/
│   └── index.py          # Vercel serverless entry point
├── backend/              # Your FastAPI code
│   ├── api/
│   ├── parser/
│   └── generator/
├── frontend/             # Static frontend files
│   ├── index.html
│   └── config.js
├── requirements.txt      # Python dependencies (root level for Vercel)
└── vercel.json          # Vercel configuration
```

## 🔧 How It Works

### Backend (Python Serverless Functions)

- **Entry Point**: `api/index.py`
- **Routes**: All `/api/*` requests go to the FastAPI backend
- **Serverless**: Each API call runs as a serverless function
- **Cold Starts**: ~1-2 seconds on first request, then fast

### Frontend (Static)

- **Files**: Everything in `frontend/` directory
- **Routes**: All other requests serve static files
- **CDN**: Cached globally for fast loading

### Configuration

**vercel.json** tells Vercel:
1. Build Python backend from `api/index.py`
2. Serve static files from `frontend/`
3. Route `/api/*` to Python functions
4. Route everything else to frontend

## 🌐 After Deployment

Once deployed, your app will be available at:
```
https://your-app-name.vercel.app
```

### Test Your Deployment

1. Visit your Vercel URL
2. Try uploading an n8n workflow JSON file
3. Click "Convert to Python"
4. Download the generated code

### API Endpoints

Your API will be available at:
- `https://your-app.vercel.app/api/health`
- `https://your-app.vercel.app/api/convert`
- `https://your-app.vercel.app/api/validate`
- `https://your-app.vercel.app/api/supported-nodes`

## 🔄 Continuous Deployment

Vercel automatically:
- ✅ Deploys every `git push` to your main branch
- ✅ Creates preview deployments for pull requests
- ✅ Updates your production URL
- ✅ Provides deployment logs and analytics

## ⚡ Performance

### Vercel Free Tier Includes:
- **Bandwidth**: 100 GB/month
- **Function Executions**: 100 GB-hours/month
- **Function Duration**: 10 seconds max per request
- **Global CDN**: Automatic
- **SSL**: Automatic HTTPS

This is plenty for a personal project or MVP!

## 🎨 Custom Domain (Optional)

To use your own domain:

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your domain (e.g., `n8n-converter.yourdomain.com`)
4. Update DNS records as shown
5. Wait for SSL certificate (automatic)

## 🐛 Troubleshooting

### Build Fails

**Check Python version:**
Vercel uses Python 3.9 by default. Create `runtime.txt` if you need specific version:
```
python-3.11
```

**Check logs:**
```bash
vercel logs
```

### API Not Working

1. Test the health endpoint: `https://your-app.vercel.app/api/health`
2. Check browser console for errors
3. Check Vercel function logs in dashboard

### Cold Starts

First request may be slow (~1-2 seconds). Subsequent requests are fast.

**To reduce cold starts:**
- Upgrade to Vercel Pro ($20/month) for faster cold starts
- Use edge caching (automatic on Vercel)
- Keep functions small and fast

### CORS Issues

Already configured to allow all origins in `backend/api/main.py`:
```python
allow_origins=["*"]
```

For production, you may want to restrict this:
```python
allow_origins=["https://your-domain.com"]
```

## 📊 Monitoring

### Vercel Dashboard

View in real-time:
- Deployments
- Function logs
- Analytics
- Performance metrics

### Access Logs

```bash
# View recent logs
vercel logs

# Stream logs in real-time
vercel logs --follow

# View production logs
vercel logs --prod
```

## 💰 Cost

### Free Tier (Perfect for MVP)
- **Cost**: $0/month
- **Limits**: 100 GB bandwidth, 100 GB-hours compute
- **Features**: All core features included

### Pro Tier (For Production)
- **Cost**: $20/month per member
- **Limits**: 1 TB bandwidth, 1000 GB-hours compute
- **Features**: Faster builds, more domains, priority support

## 🔒 Environment Variables (Future)

If you need to add secrets or config:

```bash
# Via CLI
vercel env add SECRET_KEY

# Or in dashboard
Settings → Environment Variables
```

Then use in code:
```python
import os
secret = os.getenv('SECRET_KEY')
```

## 📝 Local Development

To test locally with Vercel's environment:

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
vercel dev
```

This runs your app locally but simulates Vercel's environment.

## 🚀 Deploy Updates

Every time you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
```

Vercel automatically deploys! Check dashboard for status.

## ✅ Post-Deployment Checklist

- [ ] Visit your Vercel URL
- [ ] Upload a sample n8n workflow
- [ ] Test conversion
- [ ] Test download functionality
- [ ] Check API health endpoint
- [ ] Test validation feature
- [ ] Check Vercel function logs
- [ ] Set up custom domain (optional)
- [ ] Configure analytics (optional)

## 🎯 Next Steps

1. **Share your URL** - Your app is live!
2. **Test with real workflows** - Upload your n8n workflows
3. **Monitor usage** - Check Vercel dashboard
4. **Upgrade if needed** - Pro tier for production scale

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Functions](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)

## 🆘 Need Help?

- **Vercel Support**: https://vercel.com/support
- **Project Issues**: [GitHub Issues](https://github.com/yourusername/n8n-to-code-webapp/issues)
- **Vercel Community**: https://github.com/vercel/vercel/discussions

---

**Your n8n to Python Converter is now deployable with a single click! 🎉**

Just push to GitHub and Vercel handles the rest!
