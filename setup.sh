#!/bin/bash

# Exit on error
set -e

echo "Starting Invoice Generator setup..."

# Copy environment file
echo "Copying environment file..."
cp env.example .env

# Update .env with database settings
echo "Updating .env with default settings..."

# Set default values in .env file
echo "DEBUG=True" >> .env
echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
echo "DATABASE_URL=postgres://postgres:postgres@db:5432/invoice_generator" >> .env
echo "SECRET_KEY=your-secret-key-here-change-in-production" >> .env

echo "Starting Docker services..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Create migrations for dashboard app
echo "Creating migrations for dashboard app..."
docker-compose exec web python manage.py makemigrations dashboard

# Run migrations
echo "Running migrations..."
docker-compose exec web python manage.py migrate

# Create superuser
echo "Creating superuser..."
docker-compose exec web python manage.py shell << EOF
from django.contrib.auth.models import User
try:
    User.objects.create_superuser('admin', 'cameron5237@gmail.com', 'testpassword')
except Exception as e:
    print(f"Superuser creation failed: {str(e)}")
EOF

# Show completion message
echo "Setup complete!"
echo "You can now access the application at:"
echo "- Admin: http://localhost:8000/admin/ (login: admin/testpassword)"
echo "- API: http://localhost:8000/api/"
echo "- Dashboard: http://localhost:8000/dashboard/"
