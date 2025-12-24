# Smart City Backend - Deployment Guide

## 🚀 Quick Start (Development)

### 1. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.dev .env
# Edit .env with your settings
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/api/dashboard/

---

## 🐳 Docker Deployment

### Prerequisites

-   Docker & Docker Compose installed
-   `.env` file configured

### Build and Run

```bash
# Copy production env template
cp .env.production .env
# Edit .env with your production values

# Build and start services
docker-compose up --build -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Check Logs

```bash
docker-compose logs -f web
```

### Stop Services

```bash
docker-compose down
```

---

## 🔒 Production Deployment

### 1. Environment Variables

**Required:**

-   `SECRET_KEY`: Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
-   `DEBUG`: Set to `False`
-   `ALLOWED_HOSTS`: Comma-separated list of your domains
-   `DATABASE_URL`: PostgreSQL connection string
-   `N8N_TRAFFIC_WEBHOOK`: Your n8n traffic webhook URL
-   `N8N_REPORT_WEBHOOK`: Your n8n report webhook URL

### 2. Security Checklist

✅ Set `DEBUG=False`  
✅ Generate strong `SECRET_KEY`  
✅ Configure `ALLOWED_HOSTS` with your domain  
✅ Use PostgreSQL (not SQLite)  
✅ Set `CORS_ALLOW_ALL_ORIGINS=False` and specify allowed origins  
✅ Enable HTTPS  
✅ Configure firewall rules  
✅ Set up regular database backups

### 3. Database Setup

**PostgreSQL with Docker:**

```bash
docker-compose up -d db
```

**Manual PostgreSQL:**

```bash
sudo -u postgres psql
CREATE DATABASE smart_city_db;
CREATE USER smart_city_user WITH PASSWORD 'your_password';
ALTER ROLE smart_city_user SET client_encoding TO 'utf8';
ALTER ROLE smart_city_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE smart_city_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smart_city_db TO smart_city_user;
\q
```

### 4. Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Run with Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 60 core.wsgi:application
```

---

## 📡 API Endpoints

| Method | Endpoint                   | Description               |
| ------ | -------------------------- | ------------------------- |
| POST   | `/api/check-traffic/`      | Check traffic at location |
| POST   | `/api/webhook/save-stats/` | n8n webhook receiver      |
| GET    | `/api/dashboard/`          | Dashboard data            |
| POST   | `/api/reports/create/`     | Create citizen report     |
| GET    | `/api/reports/`            | List reports              |
| GET    | `/admin/`                  | Django admin              |

---

## 🧪 Testing

### Test Traffic Check

```bash
curl -X POST http://localhost:8000/api/check-traffic/ \
  -H "Content-Type: application/json" \
  -d '{"location": "Main Street"}'
```

### Test Dashboard

```bash
curl http://localhost:8000/api/dashboard/
```

### Test Webhook (Simulate n8n)

```bash
curl -X POST http://localhost:8000/api/webhook/save-stats/ \
  -H "Content-Type: application/json" \
  -d '{
    "energyOptimizationData": {
      "total_consumption": 1500.5,
      "avg_power": 250.0,
      "voltage_stats": {"min": 220, "max": 240, "avg": 230},
      "anomalies_detected": false
    },
    "wasteTrackingData": {
      "avg_fill_level": 65.5,
      "critical_count": 2,
      "warning_count": 5,
      "warning_locations": ["Zone A", "Zone B"]
    }
  }'
```

---

## 📊 Monitoring

### Check Container Health

```bash
docker-compose ps
```

### View Logs

```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Database Backup

```bash
docker-compose exec db pg_dump -U postgres smart_city_db > backup_$(date +%Y%m%d).sql
```

### Database Restore

```bash
cat backup_20231223.sql | docker-compose exec -T db psql -U postgres smart_city_db
```

---

## 🔧 Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database connection
docker-compose exec web python manage.py dbshell
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Permission Errors

```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

---

## 📝 Environment Variables Reference

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=domain.com,www.domain.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname

# n8n Webhooks
N8N_TRAFFIC_WEBHOOK=https://n8n.com/webhook/traffic
N8N_REPORT_WEBHOOK=https://n8n.com/webhook/report

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://domain.com
```

---

## 📦 Tech Stack

-   **Backend:** Django 5.0+
-   **API:** Django REST Framework
-   **Database:** PostgreSQL 15
-   **Server:** Gunicorn
-   **Container:** Docker & Docker Compose
-   **n8n:** Workflow automation

---

## 🤝 Support

For issues and questions:

1. Check logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure n8n webhooks are accessible
4. Check database connection

---

## 📄 License

This project is for Smart City management purposes.
