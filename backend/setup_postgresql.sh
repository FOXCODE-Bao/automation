#!/bin/bash

# Smart City Backend - PostgreSQL Setup Script
# This script helps set up PostgreSQL and migrate the database

set -e  # Exit on error

echo "🚀 Smart City Backend - PostgreSQL Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit .env and configure:"
    echo "   - DATABASE_URL (PostgreSQL connection string)"
    echo "   - SECRET_KEY (Django secret key)"
    echo "   - N8N_TRAFFIC_WEBHOOK (n8n webhook URL)"
    echo ""
    read -p "Press Enter after you've configured .env to continue..."
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating venv..."
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ venv not found. Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created and activated"
    fi
else
    echo "✅ Virtual environment is active"
fi

echo ""

# Install/upgrade dependencies
echo "📦 Installing/upgrading dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check PostgreSQL connection
echo "🔌 Checking database connection..."
python manage.py check --database default
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo ""
    echo "Please check your DATABASE_URL in .env file:"
    echo "Format: postgresql://username:password@host:port/database"
    exit 1
fi

echo ""

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Migrations completed"
echo ""

# Create superuser prompt
echo "👤 Create admin superuser?"
read -p "Do you want to create a superuser now? (y/n): " create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
    echo "✅ Superuser created"
else
    echo "ℹ️  Skipped. You can create one later with: python manage.py createsuperuser"
fi

echo ""
echo "✨ Setup Complete!"
echo ""
echo "📊 Database Models Created:"
echo "   - TrafficAnalysis (stores check-traffic results)"
echo "   - TrafficLog (legacy traffic logs)"
echo "   - EnergyLog (energy optimization data)"
echo "   - WasteLog (waste tracking data)"
echo "   - CitizenReport (citizen reports)"
echo ""
echo "🎯 Next Steps:"
echo "   1. Start the development server:"
echo "      python manage.py runserver"
echo ""
echo "   2. Access admin panel:"
echo "      http://localhost:8000/admin/"
echo ""
echo "   3. Test the traffic analysis API:"
echo "      curl -X POST http://localhost:8000/api/check-traffic/ \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"location\": \"Le Van Hien, Ngu Hanh Son, Da Nang\"}'"
echo ""
echo "   4. Check saved data in admin:"
echo "      http://localhost:8000/admin/api/trafficanalysis/"
echo ""
echo "📚 Documentation:"
echo "   - PostgreSQL Setup: POSTGRESQL_SETUP.md"
echo "   - Data Flow: TRAFFIC_DATA_FLOW.md"
echo "   - Deployment: DEPLOYMENT.md"
echo ""
