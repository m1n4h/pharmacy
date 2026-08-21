# 💊 Pharmacy Management System

A comprehensive, enterprise-grade pharmacy management system built with FastAPI and PostgreSQL. Designed to automate pharmacy operations including inventory management, sales, purchases, batch tracking, and analytics.

## ✨ Features

### 🔐 Security & Authentication
- JWT-based authentication with refresh tokens
- Role-based access control (Admin, Pharmacist, Cashier, Accountant)
- Rate limiting (60 req/min globally, 5 login attempts/min)
- Protection against XSS, CSRF, SQL injection, and brute force attacks
- Comprehensive request logging and audit trails
- Secure password hashing with bcrypt

### 📦 Inventory Management
- Real-time stock tracking
- Batch/lot management with FIFO (First In, First Out)
- Expiry date tracking and alerts
- Low stock notifications
- Stock adjustment capabilities
- Barcode support

### 💰 Sales & Billing (POS)
- Fast medicine search
- Multi-item cart management
- Automatic price fetching
- Discount support (flat or percentage)
- Multiple payment methods (cash, card, digital)
- Professional invoice generation (PDF)
- Automatic stock deduction by batch

### 🛒 Purchase Management
- Purchase invoice creation
- Multi-medicine purchase entries
- Batch details tracking
- Automatic stock updates
- Supplier assignment
- Purchase history and returns

### 👥 Supplier Management
- Supplier database
- Contact information tracking
- Purchase history per supplier
- Supplier performance analytics

### 📊 Reports & Analytics
- Daily/monthly sales reports
- Top selling items
- Profit analysis
- Inventory reports (current stock, low stock, expired items)
- Purchase reports by supplier
- Export to PDF and CSV

### 🎯 Dashboard
- Total medicines overview
- Low stock alerts
- Near-expiry items
- Daily sales summary
- Top selling items visualization
- Real-time analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip or uv package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd pharmacy-management-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up the database**
```bash
# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py
```

6. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 🐳 Docker Deployment

### Using Docker Compose

1. **Start all services**
```bash
docker-compose up -d
```

2. **Run migrations**
```bash
docker-compose exec app alembic upgrade head
```

3. **Create admin user**
```bash
docker-compose exec app python create_admin.py
```

The application will be available at `http://localhost:8000`

### Stop services
```bash
docker-compose down
```

## 📚 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗️ Project Structure

```
pharmacy-management-system/
├── alembic/                 # Database migrations
│   └── versions/           # Migration files
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core configuration
│   ├── db/                 # Database setup
│   ├── middleware/         # Custom middleware
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
├── data/                   # Sample data files
├── docs/                   # Documentation
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker composition
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
└── create_admin.py         # Admin user creation script
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Application
APP_NAME=Pharmacy Management System
APP_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pharmacy_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_DAYS=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
LOGIN_RATE_LIMIT_PER_MINUTE=5

# Password Policy
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, settings configuration |

## 🛡️ Security Features

- **Authentication**: JWT tokens with automatic refresh
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Prevents brute force and DDoS attacks
- **Security Headers**: CORS, CSP, X-Frame-Options, etc.
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **Password Security**: Bcrypt hashing with salt
- **Request Logging**: All requests logged for audit

## 📊 Database Schema

Main entities:
- **Users**: Authentication and role management
- **Medicines**: Medicine catalog with details
- **Batches**: Batch/lot tracking with expiry dates
- **Suppliers**: Supplier information
- **Purchases**: Purchase transactions and items
- **Sales**: Sales transactions and items
- **Inventory**: Real-time stock tracking
- **Settings**: System configuration

## 📈 Performance

- Handles 10k-50k medicine records efficiently
- Fast search operations (<200ms)
- Optimized database queries with proper indexing
- Connection pooling for database
- 99% uptime target

## 🔄 Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues and questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review the [Requirements Document](docs/requirements.md)
- Check application logs in `security.log`

## 🗺️ Roadmap

### Current Version (v1.0.0)
- ✅ Core pharmacy operations
- ✅ Inventory management
- ✅ Sales and purchase tracking
- ✅ Batch management
- ✅ Reports and analytics

## 🏥 Built For

Single pharmacy operations with plans to scale to multi-pharmacy chains. Suitable for:
- Independent pharmacies
- Hospital pharmacies
- Retail pharmacy chains
- Medical stores

---

**Version**: 1.0.0  
**Last Updated**: November 2025
