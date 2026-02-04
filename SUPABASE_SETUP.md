# Supabase Setup Guide for Hyperlynx Backend

This guide will walk you through setting up your Supabase database and connecting it to the Django application.

## Step 1: Create a Supabase Account

1. Visit https://supabase.com
2. Click "Sign Up"
3. Use your email, GitHub, or Google account
4. Verify your email address

## Step 2: Create a New Project

1. Go to https://supabase.com/dashboard
2. Click on "New Project" button
3. Fill in the project details:
   - **Name**: `hyperlynx` (or your preferred name)
   - **Database Password**: Create a strong password (you'll need this!)
   - **Region**: Choose closest to your location
4. Click "Create new project"
5. Wait for the project to initialize (2-5 minutes)

## Step 3: Get Your Database Credentials

Once your project is created:

1. Click on your project name to open it
2. Go to **Settings** (gear icon) → **Database**
3. You'll see a section called "Connection info"
4. Copy these values:
   ```
   Host: [project-id].supabase.co
   Port: 5432
   Database: postgres
   User: postgres
   Password: [your-database-password]
   ```

## Step 4: Configure Django

1. In the `Hyperlynx_backend` directory, create or edit the `.env` file:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Database
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-strong-password-here
SUPABASE_DB_HOST=xxxxx.supabase.co
SUPABASE_DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

Replace the values with your actual Supabase credentials.

## Step 5: Run Migrations

With your virtual environment activated:

```bash
# Ensure you're in the Hyperlynx_backend directory
cd Hyperlynx_backend

# Run migrations to create tables in Supabase
python manage.py migrate
```

This will:
- Create all necessary Django tables in your Supabase database
- Set up authentication, sessions, and other Django features

## Step 6: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Step 7: Start the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin/` and log in with your superuser credentials!

## Verifying the Connection

### Method 1: Django Admin
- Go to `http://localhost:8000/admin/`
- Log in with superuser credentials
- You should see tables from your Supabase database

### Method 2: Django Shell
```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.auth.models import User
print(User.objects.all())  # Should return empty queryset initially
```

### Method 3: Direct Database Check
You can also check in Supabase dashboard:
1. Go to your project
2. Click "SQL Editor" in the left sidebar
3. Run this query:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see Django tables like `auth_user`, `auth_group`, etc.

## Troubleshooting

### Connection Refused Error
```
Error: could not connect to server: Connection refused
```

**Solutions:**
- Verify `.env` file has correct host (should include `.supabase.co`)
- Check password is correct (no special character issues)
- Ensure your project is active in Supabase dashboard
- Check internet connection

### Authentication Failed
```
Error: FATAL: invalid password for user "postgres"
```

**Solutions:**
- Double-check password in `.env` file
- Go to Supabase → Settings → Database → Reset password if needed
- After reset, update `.env` with new password
- Run migrations again

### SSL Certificate Error
```
Error: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
This is handled in `settings.py` with `'sslmode': 'require'`. If still issues:
- Update psycopg2: `pip install --upgrade psycopg2-binary`

### Database Already Exists Error
```
Error: database "postgres" already exists
```

**Solution:**
This is normal - Supabase creates the `postgres` database by default. The error shouldn't occur if using correct credentials.

## Important Notes

⚠️ **Security:**
- Never commit `.env` file to Git (it's in `.gitignore`)
- Use strong passwords for Supabase
- Rotate passwords regularly
- Use environment variables in production

⚠️ **Supabase Free Tier Limits:**
- Limited concurrent connections
- 500 MB database size
- Backup limitations
- See https://supabase.com/pricing for full details

## Next Steps

Once database is connected:

1. **Create API Endpoints**
   - Add more models in `users/models.py`
   - Create serializers in `users/serializers.py`
   - Add views in `users/views.py`

2. **Add Authentication**
   - JWT tokens are already configured
   - Test with `POST /api/token/`

3. **Deploy**
   - Use Vercel, Heroku, or Railway for hosting
   - Update `ALLOWED_HOSTS` with your domain
   - Set `DEBUG=False` in production

## Useful Resources

- Supabase Docs: https://supabase.com/docs
- Supabase SQL Editor: https://supabase.com/dashboard
- Django PostgreSQL: https://docs.djangoproject.com/en/6.0/ref/databases/#postgresql-notes
- DRF Guide: https://www.django-rest-framework.org/

## Support

For Supabase issues:
- Check Supabase status: https://status.supabase.com
- Visit Supabase Discord: https://discord.supabase.com
- Read documentation: https://supabase.com/docs

For Django issues:
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
