# Deployment Guide - EXML to XML Converter

This guide covers various deployment options for your Django EXML converter application.

## 📁 Files to Upload

Upload these files/folders to your hosting platform:
```
exml_converter_project/
converter/
templates/
manage.py
requirements.txt
Dockerfile
docker-compose.yml
gunicorn.conf.py
```

**⚠️ Do NOT upload:**
- `__pycache__/` folders
- `db.sqlite3` (will be created on server)
- `.gitignore`
- `DEPLOYMENT.md` (optional)

## 🚀 Deployment Options

### Option 1: PythonAnywhere (Easiest)

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com/)
2. **Create a Web App**:
   - Choose Django framework
   - Python 3.9+
3. **Upload files** via drag & drop or git
4. **Configure virtual environment**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Set WSGI file** to point to your project
6. **Reload web app**

### Option 2: Heroku

1. **Install Heroku CLI**
2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```
3. **Add Procfile**:
   ```
   web: gunicorn exml_converter_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3
   ```
4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy"
   git push heroku main
   ```

### Option 3: DigitalOcean/App Platform

1. **Create App** on DigitalOcean
2. **Choose Django** template
3. **Upload files** or connect GitHub repo
4. **Configure environment variables**:
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.com`
5. **Deploy**

### Option 4: VPS (Ubuntu)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# 3. Clone/upload your files
git clone <your-repo> /var/www/exml-converter
cd /var/www/exml-converter

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure Django
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Create systemd service
sudo nano /etc/systemd/system/exml-converter.service
```

Service file content:
```ini
[Unit]
Description=EXML Converter Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/exml-converter
Environment="PATH=/var/www/exml-converter/venv/bin"
ExecStart=/var/www/exml-converter/venv/bin/gunicorn --config gunicorn.conf.py exml_converter_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Start service
sudo systemctl start exml-converter
sudo systemctl enable exml-converter

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/exml-converter
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /var/www/exml-converter/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 5: Docker Deployment

```bash
# Build and run
docker-compose up -d

# Or with Docker directly
docker build -t exml-converter .
docker run -p 8000:8000 exml-converter
```

## 🔧 Production Settings

Before deploying, update `exml_converter_project/settings.py`:

```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database (optional - for production use PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exml_converter',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## 🌐 Environment Variables

Set these in your hosting platform:
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com,www.your-domain.com`
- `SECRET_KEY=your-secret-key` (generate new one)

## 📋 Pre-Deployment Checklist

- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set `DEBUG = False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure database (if needed)
- [ ] Set up static files serving
- [ ] Test locally with production settings
- [ ] Backup any existing data

## 🧪 Testing Deployment

1. **Visit your domain** - should load the converter
2. **Test conversion** - try converting EXML to XML
3. **Check API endpoints** - `/api/` and `/examples/`
4. **Verify static files** - CSS should load properly

## 🔍 Troubleshooting

### 500 Internal Server Error
- Check Django logs: `python manage.py runserver` locally
- Verify `ALLOWED_HOSTS` setting
- Check file permissions

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Configure web server to serve `/static/`

### Database Issues
- Run `python manage.py migrate`
- Check database connection settings

## 📞 Support

For hosting-specific issues, refer to:
- PythonAnywhere: [docs.pythonanywhere.com](https://docs.pythonanywhere.com/)
- Heroku: [devcenter.heroku.com](https://devcenter.heroku.com/)
- DigitalOcean: [docs.digitalocean.com](https://docs.digitalocean.com/)

## 🚀 Quick Deploy (Recommended)

For fastest deployment, use **PythonAnywhere**:
1. Free tier available
2. Django support built-in
3. No server management required
4. Deploy in under 10 minutes
