#!/usr/bin/env bash
# Exit immediately on error
set -o errexit

echo "========================================="
echo "🌱 Starting Plantica Backend Build on Render"
echo "========================================="

# 1. Upgrade pip and install production requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Navigate to Django root if in root repository
if [ -f "plantica_core/manage.py" ]; then
    cd plantica_core
fi

# 3. Run database migrations
echo "📦 Running Database Migrations..."
python manage.py makemigrations --no-input || true
python manage.py migrate --no-input || true

# 4. Collect static files
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --no-input --clear

echo "========================================="
echo "✅ Build Process Completed Successfully!"
echo "========================================="
