# VERCEL ENVIRONMENT VARIABLES SETUP GUIDE

This file contains all the environment variables you need to add to Vercel for the Hyperlynx Backend API to work.

## How to Add to Vercel:

1. Go to: https://vercel.com/dashboard
2. Select your project: **Hyperlynx_backend**
3. Click **Settings** → **Environment Variables**
4. Copy each variable below and paste it into Vercel (Name = Value)
5. Make sure to select: **Production**, **Preview**, and **Development**
6. Click **Save**
7. Go to **Deployments** and click **Redeploy** on the latest deployment

---

## Environment Variables to Add:

### 1. SECRET_KEY
**Name:** `SECRET_KEY`
**Value:** Generate a random string (or use): `8f7c9e2a1b5d4f3a9c2e7b1d4f8a3c5e7b2d9f4a1c6e3b8d5f2a9c7e1d4f8`

### 2. JWT_SECRET_KEY
**Name:** `JWT_SECRET_KEY`
**Value:** Generate a random string (or use): `3a7f2c9e1b4d8f5a2c6e9b1d3f8a2c5e7d1a4b8f2c6e9a3d7f1b4c8e2a5d9`

### 3. SUPABASE_DB_NAME
**Name:** `SUPABASE_DB_NAME`
**Value:** `postgres`

### 4. SUPABASE_DB_USER
**Name:** `SUPABASE_DB_USER`
**Value:** `postgres`

### 5. SUPABASE_DB_PASSWORD
**Name:** `SUPABASE_DB_PASSWORD`
**Value:** `hyperlynxisthebest`

### 6. SUPABASE_DB_HOST
**Name:** `SUPABASE_DB_HOST`
**Value:** `db.odnkvecprbozydzjbybj.supabase.co`

### 7. SUPABASE_DB_PORT
**Name:** `SUPABASE_DB_PORT`
**Value:** `5432`

### 8. CORS_ALLOWED_ORIGINS (Optional)
**Name:** `CORS_ALLOWED_ORIGINS`
**Value:** `https://your-frontend-domain.vercel.app,http://localhost:3000`

---

## Testing After Deployment:

Once all variables are added and redeployed, test your API:

- **Health Check:** `https://your-domain.vercel.app/api/health`
- **Swagger UI:** `https://your-domain.vercel.app/docs`
- **Framework Library:** `https://your-domain.vercel.app/api/framework-library`
- **Root:** `https://your-domain.vercel.app/`

---

## Generating Secure Keys (Optional):

If you want to generate your own secure SECRET_KEY and JWT_SECRET_KEY, run in PowerShell:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Run this twice to get two different random values.

---

**Your app is ready to deploy! Just add these variables and redeploy.**
