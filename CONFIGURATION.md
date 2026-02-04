# Configuration guide for Hyperlynx Backend API

## Environment Setup

### Development Environment (.env)
```
SECRET_KEY=your-development-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
```

### Production Environment (.env.production)
```
SECRET_KEY=your-super-secret-key-generate-with-django-secret-key-generator
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Generate Secret Key

To generate a secure secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use Django shell:
```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

## Database Configuration

### SQLite (Development - Default)
Already configured. Uses `db.sqlite3`

### PostgreSQL (Production Recommended)

Install PostgreSQL package:
```bash
pip install psycopg2-binary
```

Update `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/hyperlynx_db
```

Update `settings.py` to use DATABASE_URL:
```python
import dj-database-url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

## CORS Configuration

### Allowed Origins
By default, the following are allowed:
- `http://localhost:3000` (React dev server)
- `http://localhost:8000` (Django dev server)
- `http://127.0.0.1:3000`

### Add More Origins
Edit `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com
```

## JWT Configuration

### Token Lifetime
Edit `hyperlynx_backend/settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),      # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),         # 1 day
    ...
}
```

Adjust according to your security requirements:
- Shorter lifetime = More secure but more refresh requests
- Longer lifetime = Less secure but better UX

## Logging Configuration

To enable logging, add to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Static & Media Files

### Development
Static files are served automatically by Django dev server.

### Production
Run to collect static files:
```bash
python manage.py collectstatic --noinput
```

Update `settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

## Security Headers

For production, add to `settings.py`:

```python
# Security middleware
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Email Configuration

For email notifications, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## Caching

Add caching to improve performance:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

Requires: `pip install django-redis`

## Testing

Run tests:
```bash
python manage.py test
python manage.py test users
python manage.py test api
```

With coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate and set SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS_ALLOWED_ORIGINS
- [ ] Set up production database
- [ ] Configure email settings
- [ ] Run migrations on production
- [ ] Collect static files
- [ ] Set up logging
- [ ] Enable security headers
- [ ] Set up monitoring/alerts
- [ ] Backup database regularly
- [ ] Use environment variables for sensitive data

