# 🚀 Hyperlynx Backend - Complete Setup Guide

Welcome to your Django REST API with Supabase integration! This document serves as your starting point.

## 📚 Documentation Overview

We've created comprehensive documentation for you. Here's what to read first:

### 🎯 Quick Start (5-10 minutes)
1. **[SETUP_SUMMARY.md](./SETUP_SUMMARY.md)** - Quick overview and first steps
2. **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - Supabase configuration guide

### 📖 Main Documentation
- **[README.md](./README.md)** - Complete API documentation and features
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and diagrams

### 🔧 Reference Guides
- **[API_TESTING.md](./API_TESTING.md)** - API testing examples (curl, Postman, Python, JS)
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Detailed configuration options
- **[CHECKLIST.md](./CHECKLIST.md)** - Implementation and deployment checklist

## 🚀 Getting Started (First Time Setup)

### Step 1: Environment Setup
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Or on macOS/Linux
source venv/bin/activate
```

### Step 2: Create Supabase Account
1. Go to https://supabase.com
2. Sign up (free account available)
3. Create a new project
4. Wait for initialization (2-5 minutes)

### Step 3: Configure Credentials
1. Get your database credentials from Supabase Settings → Database
2. Edit `.env` file in the project root
3. Fill in these credentials:
   ```env
   SUPABASE_DB_HOST=your-project.supabase.co
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-password
   SUPABASE_DB_NAME=postgres
   SECRET_KEY=your-secret-key
   ```

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Create Admin User
```bash
python manage.py createsuperuser
```

### Step 6: Start Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## ✅ What's Included

### Backend Framework
- ✅ Django 6.0.1 - Full-featured web framework
- ✅ Django REST Framework - REST API building
- ✅ SimpleJWT - JWT authentication
- ✅ CORS Headers - Cross-origin requests
- ✅ Psycopg2 - PostgreSQL adapter

### Features
- ✅ User Registration
- ✅ JWT Authentication (login/logout)
- ✅ User Profile Management
- ✅ Health Check Endpoint
- ✅ Token Refresh
- ✅ CORS Support

### Database
- ✅ Supabase PostgreSQL (managed, free tier available)
- ✅ SSL encrypted connections
- ✅ Automatic backups
- ✅ High availability

---

## 📚 API Endpoints

### Authentication
```
POST   /api/token/              - Login (get tokens)
POST   /api/token/refresh/      - Refresh access token
```

### Users
```
POST   /api/users/register/     - Register new user
GET    /api/users/profile/      - Get your profile (auth required)
PUT    /api/users/profile/      - Update profile (auth required)
```

### System
```
GET    /api/health/             - API status check
GET    /admin/                  - Django admin panel
```

---

## 🧪 Quick API Test

### 1. Check if API is running
```bash
curl http://localhost:8000/api/health/
```

### 2. Register a user
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### 3. Get token (login)
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "SecurePass123!"
  }'
```

Response will contain `access` and `refresh` tokens. Copy the `access` token.

### 4. Get your profile
```bash
curl http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

See **[API_TESTING.md](./API_TESTING.md)** for more examples!

---

## 📁 Project Structure

```
Hyperlynx_backend/
├── hyperlynx_backend/          # Main project settings
│   ├── settings.py             # Django configuration
│   ├── urls.py                 # URL routing
│   ├── wsgi.py                 # WSGI config
│   └── asgi.py                 # ASGI config
│
├── users/                      # User management app
│   ├── views.py                # RegisterView, ProfileView
│   ├── serializers.py          # Data serializers
│   ├── urls.py                 # User routes
│   └── migrations/             # Database migrations
│
├── api/                        # General API app
│   ├── views.py                # HealthCheckView
│   ├── urls.py                 # API routes
│   └── migrations/             # Migrations
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (local)
├── .env.example                # Environment template
│
├── README.md                   # API documentation
├── SUPABASE_SETUP.md          # Supabase guide
├── SETUP_SUMMARY.md           # Quick reference
├── ARCHITECTURE.md             # System architecture
├── API_TESTING.md              # Testing guide
├── CONFIGURATION.md            # Configuration options
├── CHECKLIST.md                # Implementation checklist
└── START_HERE.md              # This file
```

---

## 🔑 Key Features Explained

### JWT Authentication
- Access token (60 minutes): Use for API requests
- Refresh token (1 day): Use to get new access token
- Automatic expiration prevents unauthorized access
- See **[CONFIGURATION.md](./CONFIGURATION.md)** to adjust lifetime

### CORS Support
- Configured for local development
- Update for production domain
- See **[CONFIGURATION.md](./CONFIGURATION.md)** for details

### User Serialization
- Password hashing (PBKDF2)
- Email validation
- Password confirmation check
- Extensible for custom fields

---

## 🛠️ Common Commands

```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate

# Django migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Django shell
python manage.py shell

# Run tests
python manage.py test

# Access database directly
python manage.py dbshell

# Create new app
python manage.py startapp app_name
```

---

## 🚨 Troubleshooting

### "Could not connect to database"
→ Check `.env` file Supabase credentials in **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**

### "Module not found"
→ Run `pip install -r requirements.txt`

### "Port already in use"
→ Use different port: `python manage.py runserver 8001`

### Virtual environment issues
→ Recreate: `python -m venv venv` then reinstall dependencies

---

## 📋 Quick Checklist

Before running the first time:
- [ ] Created Supabase account
- [ ] Got database credentials
- [ ] Updated `.env` file
- [ ] Activated virtual environment
- [ ] Ran migrations
- [ ] Created superuser

---

## 🔐 Security Notes

⚠️ **Important for Production:**
- Never commit `.env` file to Git (it's in `.gitignore`)
- Change `SECRET_KEY` for production
- Set `DEBUG=False` for production
- Use strong database password
- Enable HTTPS/SSL
- Update `ALLOWED_HOSTS` with your domain

See **[CONFIGURATION.md](./CONFIGURATION.md)** for deployment checklist.

---

## 🎓 Learning Resources

### Official Documentation
- **Django**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Supabase**: https://supabase.com/docs
- **JWT**: https://github.com/jpadilla/pyjwt

### Recommended Reading Order
1. **[SETUP_SUMMARY.md](./SETUP_SUMMARY.md)** - 5 minutes
2. **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - 10 minutes
3. **[README.md](./README.md)** - 15 minutes
4. **[API_TESTING.md](./API_TESTING.md)** - Testing
5. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - How it works
6. **[CONFIGURATION.md](./CONFIGURATION.md)** - Advanced setup

---

## 📞 Support & Help

### Need Help?
1. Check relevant documentation above
2. Review examples in **[API_TESTING.md](./API_TESTING.md)**
3. Check **[CONFIGURATION.md](./CONFIGURATION.md)** for troubleshooting
4. Search Django/DRF documentation

### For Supabase Issues
- Visit https://supabase.com/docs
- Join Supabase Discord: https://discord.supabase.com
- Check status: https://status.supabase.com

### For Django Issues
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Stack Overflow tags: #django #djangorestframework

---

## 🚀 Next Steps

### Immediate (This Week)
1. Set up Supabase account
2. Configure `.env` file
3. Run migrations
4. Test API endpoints

### Short Term (This Month)
1. Add custom models
2. Implement additional endpoints
3. Add comprehensive tests
4. Set up frontend integration

### Long Term (Future)
1. Deploy to production
2. Set up CI/CD pipeline
3. Add monitoring and logging
4. Implement advanced features

---

## 📊 Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.8+ |
| **Framework** | Django 6.0 |
| **REST API** | Django REST Framework 3.16 |
| **Auth** | SimpleJWT (JWT tokens) |
| **Database** | PostgreSQL (via Supabase) |
| **CORS** | django-cors-headers |
| **DB Adapter** | psycopg2 |

---

## ✨ Features Included

- ✅ RESTful API design
- ✅ JWT token authentication
- ✅ User registration & login
- ✅ Profile management
- ✅ CORS support
- ✅ Environment configuration
- ✅ Supabase integration
- ✅ Health check endpoint
- ✅ Admin dashboard
- ✅ Database migrations
- ✅ Comprehensive documentation

---

## 🎯 What to Do Right Now

1. **Open [SETUP_SUMMARY.md](./SETUP_SUMMARY.md)** for quick start
2. **Or open [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** for Supabase setup
3. **Then follow the steps** to get your API running

---

## 📌 Version Information

```
Project: Hyperlynx Backend API
Framework: Django 6.0.1
DRF: 3.16.1
JWT: SimpleJWT 5.5.1
Database: Supabase PostgreSQL
Python: 3.8+
Created: January 30, 2026
```

---

**Questions? Check the documentation files listed above!**

**Ready to start? Open [SETUP_SUMMARY.md](./SETUP_SUMMARY.md) now!** 🚀
