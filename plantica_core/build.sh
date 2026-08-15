#!/usr/bin/env bash
# Exit immediately on error
set -o errexit

echo "========================================="
echo "🌱 Starting Plantica Backend Build on Render"
echo "========================================="

# 1. Upgrade pip and install production requirements
python -m pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
fi

# 2. Run database migrations
echo "📦 Running Database Migrations..."
python manage.py makemigrations --no-input || true
python manage.py migrate --no-input

# 3. Collect static files
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --no-input --clear

echo "========================================="
echo "✅ Build Process Completed Successfully!"
echo "========================================="
