# AI4SupplyChain Backend

Backend API for AI-powered inventory management system built with FastAPI, SQLModel, and SQLite.

## Quick Start

### 1. Install Dependencies

```bash
# Install UV package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd backend
uv sync
```

### 2. Configure Environment

```bash
# Copy environment template
cp ../.env.example ../.env

# Edit .env file with your settings (optional for development)
```

### 3. Generate Sample Data

```bash
# Generate sample data for testing
uv run python scripts/generate_sample_data.py
```

### 4. Run Development Server

```bash
# Start the API server
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

The backend follows a 4-layer architecture:

### Layer 1: Data Foundation (`src/data/`)
- **`models.py`**: SQLModel table definitions and API schemas
- **`base.py`**: Base classes and common functionality
- **`database.py`**: Database setup and connection management

### Layer 2: Business Logic (`src/services/`)
- **`inventory_service.py`**: Product and inventory management
- **`transaction_service.py`**: Transaction processing and inventory updates
- **`supplier_service.py`**: Supplier management and performance tracking
- **`location_service.py`**: Location/warehouse management

### Layer 4: API (`src/api/`)
- **`main.py`**: FastAPI application and configuration
- **`dependencies.py`**: Common dependencies and utilities
- **`products.py`**: Product management endpoints
- **`inventory.py`**: Inventory tracking endpoints
- **`suppliers.py`**: Supplier management endpoints
- **`locations.py`**: Location management endpoints
- **`transactions.py`**: Transaction processing endpoints

## API Endpoints

### Products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/` - List products (with filtering)
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/sku/{sku}` - Get product by SKU
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Deactivate product
- `GET /api/v1/products/{id}/inventory` - Get product inventory

### Inventory
- `GET /api/v1/inventory/` - Get inventory levels
- `GET /api/v1/inventory/location/{id}` - Get location inventory
- `PUT /api/v1/inventory/{product_id}/{location_id}` - Update inventory
- `POST /api/v1/inventory/{product_id}/{location_id}/reserve` - Reserve inventory
- `POST /api/v1/inventory/{product_id}/{location_id}/release` - Release reservation
- `GET /api/v1/inventory/alerts/low-stock` - Get low stock alerts

### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `POST /api/v1/transactions/batch` - Create bulk transactions
- `GET /api/v1/transactions/` - List transactions (with filtering)
- `POST /api/v1/transactions/receipt` - Process stock receipt
- `POST /api/v1/transactions/shipment` - Process stock shipment
- `POST /api/v1/transactions/transfer` - Process stock transfer
- `POST /api/v1/transactions/adjustment` - Process stock adjustment

### Suppliers
- `POST /api/v1/suppliers/` - Create supplier
- `GET /api/v1/suppliers/` - List suppliers
- `GET /api/v1/suppliers/{id}` - Get supplier by ID
- `PUT /api/v1/suppliers/{id}` - Update supplier
- `DELETE /api/v1/suppliers/{id}` - Deactivate supplier
- `GET /api/v1/suppliers/{id}/products` - Get supplier products
- `GET /api/v1/suppliers/{id}/performance` - Get supplier performance

### Locations
- `POST /api/v1/locations/` - Create location
- `GET /api/v1/locations/` - List locations
- `GET /api/v1/locations/{id}` - Get location by ID
- `PUT /api/v1/locations/{id}` - Update location
- `DELETE /api/v1/locations/{id}` - Deactivate location
- `GET /api/v1/locations/{id}/inventory` - Get location inventory summary

## Database Schema

### Core Tables
- **Products**: Product master data with SKUs, categories, costs, reorder points
- **Suppliers**: Vendor information with lead times and performance metrics
- **Locations**: Warehouse/storage locations
- **Inventory**: Current stock levels by product and location
- **Transactions**: Complete audit trail of all inventory movements

### Key Relationships
- Products → Suppliers (many-to-one)
- Inventory → Products + Locations (composite unique key)
- Transactions → Products + Locations (for audit trail)

## Configuration

Key configuration options in `src/config.py`:

```python
# Database
DATABASE_URL = "sqlite:///./data/inventory.db"

# Business Rules
ALLOW_NEGATIVE_INVENTORY = False
AUTO_CREATE_INVENTORY_RECORDS = True
DEFAULT_REORDER_POINT = 10
DEFAULT_REORDER_QUANTITY = 50

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Sort imports
uv run isort src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/
```

### Adding New Features

1. **Data Models**: Add/modify models in `src/data/models.py`
2. **Business Logic**: Implement services in `src/services/`
3. **API Endpoints**: Create endpoints in `src/api/`
4. **Tests**: Add tests in `tests/`

## Sample Data

The system includes a sample data generator that creates:
- 4 suppliers with realistic contact information
- 4 locations (warehouses and retail stores)
- 8 products across different categories
- Initial inventory levels for all product-location combinations
- 30 days of transaction history

Run with: `uv run python scripts/generate_sample_data.py`

## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid input data or business rule violations
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate data (e.g., SKU already exists)
- **500 Internal Server Error**: Unexpected server errors

All errors return structured JSON responses with descriptive messages.

## Production Deployment

For production deployment:

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Consider migrating to PostgreSQL for better performance
3. **Security**: Use strong `SECRET_KEY` and enable HTTPS
4. **Monitoring**: Add logging and health check endpoints
5. **Scaling**: Use reverse proxy (nginx) and multiple workers