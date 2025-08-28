# Sales Pulse Backend API

Django REST API for the Sales Pulse application with JWT authentication, CSV data processing, and dashboard metrics.

## Features

- **JWT Authentication** with SimpleJWT
- **CSV Upload & Processing** with data validation
- **Daily Sales Aggregation** with automatic recomputation
- **Dashboard Metrics API** with filtering capabilities
- **Data Validation** (no negative values, proper date formatting)
- **Error Reporting** for invalid CSV rows

## API Endpoints

### Authentication

- `POST /api/auth/login/` - JWT login
- `POST /api/auth/logout/` - JWT logout (optional)

### Sales Data

- `POST /api/sales/upload/` - Upload and process CSV files

### Metrics

- `GET /api/metrics/summary/` - Get dashboard metrics
  - Query Parameters:
    - `date_from` (optional): Start date filter (YYYY-MM-DD)
    - `date_to` (optional): End date filter (YYYY-MM-DD)

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone and navigate to backend:**

   ```bash
   cd backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**

   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## CSV Upload Format

Expected CSV columns:

- `product_name` (string, required)
- `category` (string, optional)
- `price` (decimal, required, non-negative)
- `quantity` (integer, required, positive)
- `sold_at` (date, required, format: YYYY-MM-DD)

### Sample CSV

```csv
product_name,category,price,quantity,sold_at
Laptop Pro,Electronics,1299.99,2,2025-08-15
Wireless Mouse,Electronics,29.99,5,2025-08-15
Coffee Mug,Kitchen,12.50,3,2025-08-16
```

## API Usage Examples

### 1. Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "Random@123"}'
```

Response:

```json
{
  "success": true,
  "message": "Login successful",
  "user": {"id": 1, "username": "admin", ...},
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. Upload CSV

```bash
curl -X POST http://127.0.0.1:8000/api/sales/upload/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -F "file=@sample-sales.csv"
```

Response:

```json
{
  "success": true,
  "message": "Processed 7 rows, skipped 0 invalid rows",
  "data": {
    "processed_count": 7,
    "skipped_count": 0,
    "errors": []
  }
}
```

### 3. Get Metrics

```bash
curl -X GET http://127.0.0.1:8000/api/metrics/summary/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:

```json
{
  "success": true,
  "data": {
    "kpis": {
      "total_revenue": 4437.31,
      "total_orders": 7,
      "total_units": 24
    },
    "daily_revenue": [
      {"date": "2024-01-15", "revenue": 2749.93, "orders": 2, "units": 7}
    ],
    "top_products": [
      {"name": "Laptop Pro", "total_sales": 3899.97, "units_sold": 3}
    ]
  }
}
```

## Database Models

### Product

- `name` (CharField, unique)
- `category` (CharField)
- `price` (DecimalField)
- `created_at`, `updated_at`

### Sale

- `product` (ForeignKey to Product)
- `quantity` (PositiveIntegerField)
- `price` (DecimalField)
- `sold_at` (DateField)
- `total` (DecimalField, auto-calculated)
- `created_at`

### DailyAggregate

- `date` (DateField, unique)
- `total_revenue` (DecimalField)
- `total_orders` (PositiveIntegerField)
- `total_units` (PositiveIntegerField)
- `created_at`, `updated_at`

## Test User

For development/testing:

- Username: `admin`
- Password: `admin123` (or whatever you set)

## Data Processing Features

- **Validation**: Checks for negative values, missing fields, invalid dates
- **Error Reporting**: Detailed error messages for invalid rows
- **Product Management**: Auto-creates products or updates existing ones
- **Aggregation**: Automatically computes daily totals on upload
- **Transaction Safety**: All operations are wrapped in database transactions

## Admin Interface

Access Django admin at: `http://127.0.0.1:8000/admin/`

View and manage:

- Products
- Sales
- Daily Aggregates
- Users

## Development

- **Framework**: Django 4.2+ with Django REST Framework
- **Authentication**: JWT via SimpleJWT
- **Database**: SQLite 
- **Data Processing**: Pandas for CSV handling
