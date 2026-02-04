# Railway Deployment Guide for Hyperlynx Backend

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- Railway account ([railway.app](https://railway.app))
- Your code pushed to GitHub
- Supabase project already set up

### 2. Deploy to Railway

1. **Connect Your Repository**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `Hyperlynx_backend` repository

2. **Configure Environment Variables**
   
   In Railway project settings, add these variables:

   ```env
   SECRET_KEY=your-secret-key-generate-a-new-one
   DEBUG=False
   ALLOWED_HOSTS=.railway.app
   
   # CORS - Add your frontend URL
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
   
   # Supabase Database
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=hyperlynxisthebest
   SUPABASE_DB_HOST=db.odnkvecprbozydzjbybj.supabase.co
   SUPABASE_DB_PORT=5432
   
   # JWT Settings
   JWT_ACCESS_TOKEN_LIFETIME=60
   JWT_REFRESH_TOKEN_LIFETIME=1
   ```

3. **Railway Will Automatically**
   - Detect it's a Django project
   - Install dependencies from `requirements.txt`
   - Run migrations with the start command
   - Start the Gunicorn server

### 3. After Deployment

1. **Get Your Railway URL**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Add this to your `ALLOWED_HOSTS` environment variable

2. **Update CORS Settings**
   - Add your frontend URL to `CORS_ALLOWED_ORIGINS`

3. **Access Your API**
   - API Docs: `https://your-app.railway.app/api/docs/`
   - Health Check: `https://your-app.railway.app/api/health/`

## 📁 Files Created for Deployment

- **Procfile** - Tells Railway how to start your app
- **runtime.txt** - Specifies Python version
- **railway.json** - Railway-specific configuration
- **nixpacks.toml** - Build and deployment configuration
- **requirements.txt** - Updated with `gunicorn` and `whitenoise`

## 🔧 Key Configuration Changes

### Added to requirements.txt:
```
gunicorn==23.0.0
whitenoise==6.8.2
```

### Updated settings.py:
- Added `WhiteNoiseMiddleware` for static files
- Configured `STATIC_ROOT` for production
- Already using environment variables for sensitive data

## 🐛 Troubleshooting

### Build Fails
- Check Railway logs for specific errors
- Ensure all environment variables are set
- Verify Supabase credentials

### Database Connection Issues
- Verify Supabase host is correct: `db.odnkvecprbozydzjbybj.supabase.co`
- Check Supabase password
- Ensure Supabase allows connections from Railway

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput` (done automatically)
- Check `STATIC_ROOT` is set correctly

## 📝 Generate a New SECRET_KEY

Run in Python console:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🔗 Useful Commands

Test locally with production settings:
```bash
# Install new dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn hyperlynx_backend.wsgi
```

## ✅ Deployment Checklist

- [ ] All environment variables configured in Railway
- [ ] SECRET_KEY is different from development
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS includes Railway domain
- [ ] CORS_ALLOWED_ORIGINS includes frontend URL
- [ ] Supabase credentials are correct
- [ ] First deployment successful
- [ ] Migrations ran successfully
- [ ] API endpoints are accessible
- [ ] Swagger UI loads at `/api/docs/`

## 🎉 Your API is Now Live!

Once deployed, your backend will be accessible at:
- **Swagger UI**: `https://your-app.railway.app/api/docs/`
- **API Base**: `https://your-app.railway.app/api/`
- **Health Check**: `https://your-app.railway.app/api/health/`
