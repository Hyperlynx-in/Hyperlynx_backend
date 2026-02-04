# Flask Application - Hyperlynx Backend

A Flask REST API for framework library management with JWT authentication.

## Features
- User registration and authentication (JWT)
- Framework library management from YAML files
- PostgreSQL database support (Supabase)
- CORS enabled
- Deployed on Vercel

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT tokens
- `GET /auth/profile` - Get user profile (requires JWT)
- `PUT /auth/profile` - Update user profile (requires JWT)
- `POST /auth/refresh` - Refresh access token

### API
- `GET /api/health` - Health check
- `GET /api/framework-library` - List all frameworks
- `GET /api/framework-library?name=nist-csf-2.0` - Get specific framework

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=your-user
SUPABASE_DB_PASSWORD=your-password
SUPABASE_DB_HOST=your-host
SUPABASE_DB_PORT=6543
```

3. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

4. Run the application:
```bash
flask run
```

## Vercel Deployment

1. Push code to GitHub
2. Import project on Vercel
3. Add environment variables in Vercel dashboard
4. Deploy!

## Environment Variables for Vercel

- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key
- `SUPABASE_DB_NAME` - postgres
- `SUPABASE_DB_USER` - Your Supabase user (format: postgres.projectref)
- `SUPABASE_DB_PASSWORD` - Your Supabase password
- `SUPABASE_DB_HOST` - Pooler host (e.g., aws-0-ap-south-1.pooler.supabase.com)
- `SUPABASE_DB_PORT` - 6543
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins
