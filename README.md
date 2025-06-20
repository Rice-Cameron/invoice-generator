# Time-Tracked Invoice Generator for Freelancers

A comprehensive Django-based backend service that allows freelancers to manage clients, track time, and generate professional invoices with PDF generation and Stripe payment integration.

## 🚀 Features

- **User Management**: JWT-based authentication with multi-tenant data isolation
- **Client Management**: Full CRUD operations for client information
- **Project Management**: Organize work by projects with time tracking
- **Time Tracking**: Log billable hours with detailed descriptions
- **Invoice Generation**: Create professional PDF invoices from time entries
- **Recurring Invoices**: Schedule automatic invoice generation (weekly/monthly/quarterly)
- **Email Integration**: Send invoices directly to clients
- **Stripe Integration**: Accept online payments with Stripe checkout
- **Background Tasks**: Celery-powered scheduled tasks for automation
- **RESTful API**: Complete API with filtering, searching, and pagination

## 🏗️ Architecture

```
/invoice_generator/
├── clients/              # Client management
├── projects/             # Project management
├── time_entries/         # Time tracking
├── invoices/             # Invoice generation & PDF
├── stripe_integration/   # Payment processing
├── core/                 # User management & base models
├── templates/invoices/   # PDF & email templates
├── static/               # Static files
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Development environment
└── README.md            # This file
```

## 🛠️ Technology Stack

- **Backend**: Django 5.0.2, Django REST Framework 3.14.0
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **PDF Generation**: WeasyPrint
- **Payment Processing**: Stripe
- **Background Tasks**: Celery + Redis
- **Email**: Django email backend
- **Containerization**: Docker & Docker Compose

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (if not using Docker)

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd invoice-generator
   ```

2. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**

   ```bash
   docker-compose up -d
   ```

4. **Run migrations**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/api/

### Manual Installation

1. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Troubleshooting

#### Python Version Issues

This project requires **Python 3.11 or higher**. If you encounter version-related errors:

1. **Check your Python version:**

   ```bash
   python --version
   ```

2. **If using Python 3.9 or earlier, upgrade to Python 3.11:**

   ```bash
   # On macOS with Homebrew
   brew install python@3.11

   # Create virtual environment with Python 3.11
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Virtual Environment Issues

If you get "Couldn't import Django" errors even after activating your virtual environment:

1. **Check if virtual environment is activated:**

   ```bash
   which python
   # Should show: /path/to/your/project/venv/bin/python
   ```

2. **If you have Python aliases that override your venv:**

   ```bash
   # Check for aliases
   type python

   # If it shows an alias, remove it
   unalias python

   # Reactivate your virtual environment
   deactivate
   source venv/bin/activate
   ```

3. **Verify Django is installed in your venv:**

   ```bash
   python -m django --version
   # Should show: 5.0.2
   ```

4. **If issues persist, recreate the virtual environment:**
   ```bash
   deactivate
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Database Issues

If you encounter database connection errors:

1. **For SQLite (default for development):**

   - The project is configured to use SQLite by default
   - No additional setup required

2. **For PostgreSQL:**
   - Install PostgreSQL
   - Update your `.env` file with database credentials
   - Ensure PostgreSQL service is running

#### Migration Issues

If you encounter migration errors:

1. **Reset migrations (WARNING: This will delete your database):**

   ```bash
   rm db.sqlite3  # Only for SQLite
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **If Django internal files are missing:**
   ```bash
   pip install --force-reinstall Django==5.0.2
   python manage.py makemigrations
   python manage.py migrate
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=invoice_generator
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (Optional)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### Celery Configuration

For production, set up Celery with Redis:

```bash
# Start Celery worker
celery -A invoice_generator worker -l info

# Start Celery beat (for scheduled tasks)
celery -A invoice_generator beat -l info
```

## 📚 API Documentation

### Authentication

All API endpoints require JWT authentication except for registration.

```bash
# Register a new user
POST /api/register/
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "password2": "password123",
    "first_name": "John",
    "last_name": "Doe"
}

# Login to get tokens
POST /api/token/
{
    "email": "user@example.com",
    "password": "password123"
}

# Use the access token in headers
Authorization: Bearer <access_token>
```

### Core Endpoints

#### User Management

- `POST /api/register/` - Register new user
- `POST /api/token/` - Get JWT tokens
- `POST /api/token/refresh/` - Refresh access token
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update user profile
- `POST /api/change-password/` - Change password
- `GET /api/dashboard/` - User dashboard with statistics

#### Clients

- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client details
- `PUT /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client

#### Projects

- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project
- `GET /api/projects/by-client/{client_id}/` - Get projects by client

#### Time Entries

- `GET /api/time-entries/` - List time entries
- `POST /api/time-entries/` - Create time entry
- `GET /api/time-entries/{id}/` - Get time entry details
- `PUT /api/time-entries/{id}/` - Update time entry
- `DELETE /api/time-entries/{id}/` - Delete time entry
- `POST /api/time-entries/bulk-create/` - Bulk create time entries
- `GET /api/time-entries/by-project/{project_id}/` - Get time entries by project
- `GET /api/time-entries/summary/` - Get time entry summary

#### Invoices

- `GET /api/invoices/` - List invoices
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/{id}/` - Get invoice details
- `PUT /api/invoices/{id}/` - Update invoice
- `DELETE /api/invoices/{id}/` - Delete invoice
- `POST /api/invoices/create-from-time-entries/` - Create invoice from time entries
- `POST /api/invoices/{id}/send/` - Send invoice via email
- `GET /api/invoices/{id}/pdf/` - Download invoice PDF
- `POST /api/invoices/{id}/mark-paid/` - Mark invoice as paid
- `GET /api/invoices/summary/` - Get invoice summary
- `GET /api/invoices/overdue/` - Get overdue invoices

#### Stripe Integration (Optional)

- `GET /api/stripe/config/` - Get Stripe configuration
- `POST /api/stripe/create-payment-intent/` - Create payment intent
- `POST /api/stripe/create-checkout-session/` - Create checkout session
- `GET /api/stripe/payment-intents/` - List payment intents
- `GET /api/stripe/payment-intent-status/{id}/` - Get payment intent status
- `POST /api/stripe/webhook/` - Stripe webhook endpoint

## 💡 Usage Examples

### Creating an Invoice from Time Entries

```bash
# Create invoice from time entries
POST /api/invoices/create-from-time-entries/
{
    "client": 1,
    "project": 2,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "tax_rate": 8.5,
    "notes": "January 2024 work"
}
```

### Sending an Invoice

```bash
# Send invoice via email
POST /api/invoices/1/send/
{
    "email_subject": "Invoice for January 2024",
    "email_message": "Please find attached invoice for services rendered.",
    "send_to_client": true,
    "send_copy_to_user": true
}
```

### Creating a Stripe Payment Intent

```bash
# Create payment intent for invoice
POST /api/stripe/create-payment-intent/
{
    "invoice_id": 1
}
```

## 🔄 Scheduled Tasks

The application includes several Celery tasks for automation:

- **Recurring Invoices**: Automatically generate invoices based on client/project settings
- **Overdue Reminders**: Send reminder emails for overdue invoices
- **PDF Generation**: Background PDF generation for invoices
- **Email Sending**: Asynchronous email sending

### Setting up Scheduled Tasks

```bash
# Start Celery beat scheduler
celery -A invoice_generator beat -l info

# Start Celery worker
celery -A invoice_generator worker -l info
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test clients
python manage.py test invoices
```

## 📊 Database Schema

### Key Models

- **User**: Custom user model with freelancer-specific fields
- **Client**: Client information with recurring invoice settings
- **Project**: Project management with time tracking
- **TimeEntry**: Time tracking with billable hours
- **Invoice**: Invoice generation with PDF support
- **InvoiceItem**: Line items for invoices
- **StripePaymentIntent**: Stripe payment processing
- **StripeWebhookEvent**: Webhook event tracking

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**: Set `DEBUG=False` and configure production settings
2. **Database**: Use production PostgreSQL instance
3. **Static Files**: Configure static file serving
4. **Media Files**: Set up media file storage (AWS S3 recommended)
5. **Email**: Configure production email backend
6. **Stripe**: Use production Stripe keys
7. **SSL**: Enable HTTPS
8. **Monitoring**: Set up logging and monitoring

### Docker Production

```bash
# Build production image
docker build -t invoice-generator:prod .

# Run with production settings
docker run -d \
  -e DEBUG=False \
  -e DATABASE_URL=postgres://... \
  -p 8000:8000 \
  invoice-generator:prod
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔗 Related Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe Documentation](https://stripe.com/docs)
- [Celery Documentation](https://docs.celeryproject.org/)
- [WeasyPrint Documentation](https://weasyprint.readthedocs.io/)
