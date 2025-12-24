# PostgreSQL Setup Guide

This guide will help you configure PostgreSQL for the Smart City Backend project.

## Prerequisites

-   PostgreSQL installed on your system
-   Python environment activated

## Option 1: Local PostgreSQL Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**

```bash
brew install postgresql
brew services start postgresql
```

### 2. Create Database and User

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE smart_city_db;

# Create user
CREATE USER smart_city_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_city_db TO smart_city_user;

# Exit
\q
```

### 3. Install Python PostgreSQL Driver

```bash
pip install psycopg2-binary
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and update:

```env
DATABASE_URL=postgresql://smart_city_user:your_secure_password@localhost:5432/smart_city_db
```

## Option 2: Docker PostgreSQL Setup

### 1. Use Docker Compose

The project includes a `docker-compose.yml` with PostgreSQL configuration.

Start PostgreSQL:

```bash
docker-compose up -d db
```

### 2. Configure Environment Variables

Update `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_city_db
```

## Apply Migrations

After configuring PostgreSQL:

```bash
# Create migrations (already done)
python manage.py makemigrations

# Apply migrations to PostgreSQL
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
```

## Verify Connection

Test the database connection:

```bash
python manage.py dbshell
```

You should see the PostgreSQL prompt.

## Database Models

The project now includes these models that will be saved to PostgreSQL:

### TrafficAnalysis

Stores detailed traffic analysis results from the check-traffic endpoint:

-   Address and location
-   Congestion rate and flow speed
-   Incidents and delays
-   Status codes and colors
-   Analysis text and recommendations
-   Alternative routes
-   Alert content

### TrafficLog

Stores simplified traffic logs (legacy model)

### EnergyLog

Stores energy consumption and optimization data

### WasteLog

Stores waste management tracking data

### CitizenReport

Stores citizen-reported issues

## Accessing the Data

### Django Admin Panel

1. Create a superuser:

```bash
python manage.py createsuperuser
```

2. Run the development server:

```bash
python manage.py runserver
```

3. Access admin panel: `http://localhost:8000/admin/`

### API Endpoints

The traffic analysis data is automatically saved when you call:

-   `POST /api/check-traffic/` with `{"location": "your address"}`

## Troubleshooting

### Connection Refused

-   Ensure PostgreSQL is running: `sudo systemctl status postgresql`
-   Check if port 5432 is listening: `sudo netstat -plnt | grep 5432`

### Authentication Failed

-   Verify credentials in `.env` file
-   Check PostgreSQL pg_hba.conf for authentication method

### Migration Errors

-   Drop and recreate database if starting fresh
-   Check model definitions in `api/models.py`

## Production Considerations

1. **Use strong passwords** for database users
2. **Configure proper backups** using pg_dump
3. **Set up connection pooling** with PgBouncer
4. **Monitor database performance** with pg_stat_statements
5. **Implement proper indexes** (already configured in models)

## Environment Variables Reference

```env
# Required
DATABASE_URL=postgresql://username:password@host:port/database

# Optional (for Django)
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Next Steps

1. Configure your `.env` file with PostgreSQL credentials
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Test the API: Make a POST request to `/api/check-traffic/`
5. Check the admin panel to verify data is saved
