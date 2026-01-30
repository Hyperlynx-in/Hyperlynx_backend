# Hyperlynx Backend - Django REST API with Supabase

A complete Django REST Framework project with JWT authentication configured to use Supabase PostgreSQL database.

## Features

- ✅ Django REST Framework for building REST APIs
- ✅ JWT Authentication with SimpleJWT
- ✅ Supabase PostgreSQL Database Integration
- ✅ CORS Support for frontend integration
- ✅ User Registration and Profile Management
- ✅ Health Check Endpoint
- ✅ Environment-based Configuration

## Prerequisites

- Python 3.8+
- Supabase Account (free tier available at https://supabase.com)
- pip (Python package manager)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Hyperlynx_backend
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Supabase Database

1. **Create a Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Enter project name and password
   - Wait for project to initialize

2. **Get Database Credentials**
   - In your Supabase dashboard, go to Settings → Database
   - You'll find:
     - Host (Project URL)
     - Database name (usually "postgres")
     - Username (usually "postgres")
     - Password (the one you created)
     - Port (usually 5432)

3. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials:
   ```env
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-password
   SUPABASE_DB_HOST=xxxxx.supabase.co
   SUPABASE_DB_PORT=5432
   ```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### 7. Run Development Server
```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`



### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

## API Endpoints### 7. Run development server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT tokens (login)
- `POST /api/token/refresh/` - Refresh access token

### Users
- `POST /api/users/register/` - Register new user
- `GET /api/users/profile/` - Get user profile (requires auth)
- `PUT /api/users/profile/` - Update user profile (requires auth)

### Health Check
- `GET /api/health/` - API health check

## JWT Authentication

### Login to get tokens
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Use access token in requests
```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### Refresh access token
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

## Project Structure

```
Hyperlynx_backend/
├── hyperlynx_backend/      # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── users/                 # User management app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── migrations/
├── api/                   # Main API app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Configuration

### CORS Settings
Edit `.env` to allow specific origins:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### JWT Token Lifetime
Edit `hyperlynx_backend/settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    ...
}
```

## Development

### Create a new app
```bash
python manage.py startapp <app_name>
```

### Create migrations
```bash
python manage.py makemigrations
```

### Apply migrations
```bash
python manage.py migrate
```

### Run tests
```bash
python manage.py test
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL recommended)
5. Use a production WSGI server (gunicorn, uWSGI)
6. Enable HTTPS
7. Collect static files: `python manage.py collectstatic`

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn hyperlynx_backend.wsgi:application --bind 0.0.0.0:8000
```

## Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)

## License

Your License Here

## Support

For issues and questions, please create an issue in the repository.
