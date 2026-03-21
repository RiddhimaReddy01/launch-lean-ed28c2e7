# LaunchLens Deployment Guide

## Backend Deployment (Render)

### Prerequisites
- [Render account](https://render.com) (free tier available)
- GitHub repository with your code pushed

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Service

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `launchlens-backend`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3.13
   - **Build Command**:
     ```
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free tier (or Pro for production)

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment** and add:

```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SERPER_API_KEY=your_serper_api_key
ENVIRONMENT=production
GROQ_MODEL=openai/gpt-oss-20b
FRONTEND_URL=https://your-app.lovable.app
```

### Step 4: Deploy

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. You'll get a URL like: `https://launchlens-backend.onrender.com`

### Step 5: Verify Backend

Test health endpoint:
```bash
curl https://launchlens-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "providers": {
    "groq_key": true,
    "gemini_key": true,
    "serper_key": true,
    "supabase_url": true
  },
  "environment": "production"
}
```

---

## Frontend Deployment (Lovable)

### Option 1: Deploy via Lovable Dashboard

1. Go to [Lovable.app](https://lovable.app)
2. Click **Import Project**
3. Select **GitHub** as source
4. Connect your GitHub repository
5. Select `frontend` folder as root
6. Click **Deploy**

### Option 2: Manual Git Push to Lovable

```bash
# Add Lovable as remote
git remote add lovable git@github.com:your-username/your-repo.git

# Push to Lovable
git push lovable main
```

### Step 1: Update API Endpoint

In `frontend/src/api/client.ts`, update:

```typescript
const API_BASE = process.env.REACT_APP_API_URL ||
  'https://launchlens-backend.onrender.com';
```

### Step 2: Set Environment Variables in Lovable

In Lovable dashboard → Settings → Environment Variables:

```
REACT_APP_API_URL=https://launchlens-backend.onrender.com
```

### Step 3: Deploy

```bash
cd frontend
npm run build
```

Lovable will automatically deploy the built frontend.

---

## Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] API calls work (test decompose endpoint)
- [ ] All 10 test queries succeed
- [ ] Loading spinners show correctly
- [ ] Error boundary catches failures gracefully
- [ ] Database queries work (if saving ideas)

---

## Troubleshooting

### Backend won't start
- Check logs: Render → Service → Logs
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### API calls fail from frontend
- Check CORS in `app/main.py` includes Lovable domain
- Verify `FRONTEND_URL` is set correctly in backend
- Check browser console for CORS errors

### LLM API calls failing
- Verify API keys are correct in Render environment
- Check Groq model is enabled at https://console.groq.com/settings/project/limits
- Fallback decomposition will work even if LLMs fail

---

## Monitoring

### Backend Monitoring
- Render dashboard shows CPU/memory usage
- Check `/health` endpoint regularly
- Monitor logs for errors

### Frontend Monitoring
- Lovable dashboard shows deployment status
- Check browser console for JavaScript errors
- Monitor Network tab for API failures

---

## Production Best Practices

1. **Enable auto-deploys** in Render for main branch
2. **Set up error tracking** (Sentry recommended)
3. **Enable HTTPS** (automatic on Render/Lovable)
4. **Regular backups** of Supabase data
5. **Monitor API quotas** for Groq/Gemini
6. **Set up alerts** for high error rates

---

## Rollback Procedure

### Render
1. Go to Render dashboard
2. Click on your service
3. Go to **Deployments**
4. Click **Redeploy** on a previous deployment

### Lovable
Push a previous commit:
```bash
git revert <commit-hash>
git push lovable main
```

---

## Support

- Render docs: https://render.com/docs
- Lovable docs: https://lovable.app/docs
- LaunchLens issues: Create a GitHub issue
