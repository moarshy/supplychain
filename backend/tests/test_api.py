"""
Basic API endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI4SupplyChain Inventory Management API"
    assert "version" in data


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_system_stats(client: TestClient):
    """Test system statistics endpoint."""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "suppliers" in data
    assert "locations" in data
    assert "transactions" in data


def test_create_supplier(client: TestClient):
    """Test supplier creation endpoint."""
    supplier_data = {
        "name": "API Test Supplier",
        "contact_person": "Test Person",
        "email": "test@apisupplier.com",
        "lead_time_days": 5,
        "payment_terms": "Net 30",
        "minimum_order_qty": 10
    }
    
    response = client.post("/api/v1/suppliers/", json=supplier_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == supplier_data["name"]
    assert data["email"] == supplier_data["email"]
    assert "id" in data


def test_list_suppliers(client: TestClient, sample_supplier):
    """Test supplier listing endpoint."""
    response = client.get("/api/v1/suppliers/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_supplier.name


def test_get_supplier(client: TestClient, sample_supplier):
    """Test get supplier by ID endpoint."""
    response = client.get(f"/api/v1/suppliers/{sample_supplier.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == sample_supplier.id
    assert data["name"] == sample_supplier.name


def test_create_location(client: TestClient):
    """Test location creation endpoint."""
    location_data = {
        "name": "API Test Location",
        "code": "API",
        "address": "123 API Street, API City",
        "warehouse_type": "Test"
    }
    
    response = client.post("/api/v1/locations/", json=location_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == location_data["name"]
    assert data["code"] == location_data["code"]
    assert "id" in data


def test_list_locations(client: TestClient, sample_location):
    """Test location listing endpoint."""
    response = client.get("/api/v1/locations/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_location.name


def test_create_product(client: TestClient, sample_supplier):
    """Test product creation endpoint."""
    product_data = {
        "sku": "API-TEST-001",
        "name": "API Test Product",
        "description": "A product created via API test",
        "category": "API Test",
        "unit_cost": 25.50,
        "unit_price": 45.00,
        "reorder_point": 10,
        "reorder_quantity": 50,
        "supplier_id": sample_supplier.id
    }
    
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["sku"] == product_data["sku"]
    assert data["name"] == product_data["name"]
    assert float(data["unit_cost"]) == product_data["unit_cost"]
    assert "id" in data


def test_list_products(client: TestClient, sample_product):
    """Test product listing endpoint."""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["sku"] == sample_product.sku


def test_get_product_by_sku(client: TestClient, sample_product):
    """Test get product by SKU endpoint."""
    response = client.get(f"/api/v1/products/sku/{sample_product.sku}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["sku"] == sample_product.sku
    assert data["name"] == sample_product.name


def test_get_inventory(client: TestClient):
    """Test inventory listing endpoint."""
    response = client.get("/api/v1/inventory/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_process_stock_receipt(client: TestClient, sample_product, sample_location):
    """Test stock receipt processing."""
    response = client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": sample_product.id,
            "location_id": sample_location.id,
            "quantity": 100,
            "reference_number": "TEST-PO-001",
            "notes": "Test stock receipt",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["transaction_type"] == "IN"
    assert data["quantity"] == 100
    assert data["product_id"] == sample_product.id
    assert data["location_id"] == sample_location.id


def test_process_stock_shipment(client: TestClient, sample_product, sample_location):
    """Test stock shipment processing."""
    # First add some stock
    client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": sample_product.id,
            "location_id": sample_location.id,
            "quantity": 100,
            "user_id": "test_user"
        }
    )
    
    # Then ship some stock
    response = client.post(
        "/api/v1/transactions/shipment",
        params={
            "product_id": sample_product.id,
            "location_id": sample_location.id,
            "quantity": 25,
            "reference_number": "TEST-DO-001",
            "notes": "Test stock shipment",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["transaction_type"] == "OUT"
    assert data["quantity"] == -25
    assert data["product_id"] == sample_product.id
    assert data["location_id"] == sample_location.id


def test_list_transactions(client: TestClient):
    """Test transaction listing endpoint."""
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_transaction_summary(client: TestClient):
    """Test transaction summary endpoint."""
    response = client.get("/api/v1/transactions/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_transactions" in data
    assert "in_transactions" in data
    assert "out_transactions" in data


def test_error_handling_invalid_supplier(client: TestClient):
    """Test error handling for invalid supplier ID."""
    response = client.get("/api/v1/suppliers/99999")
    assert response.status_code == 404
    
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_error_handling_duplicate_sku(client: TestClient, sample_product, sample_supplier):
    """Test error handling for duplicate SKU."""
    product_data = {
        "sku": sample_product.sku,  # Duplicate SKU
        "name": "Duplicate Test Product",
        "unit_cost": 10.00,
        "supplier_id": sample_supplier.id
    }
    
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == 409  # Conflict
    
    data = response.json()
    assert "already exists" in data["detail"].lower()


def test_error_handling_insufficient_stock(client: TestClient, sample_product, sample_location):
    """Test error handling for insufficient stock."""
    # Try to ship more stock than available
    response = client.post(
        "/api/v1/transactions/shipment",
        params={
            "product_id": sample_product.id,
            "location_id": sample_location.id,
            "quantity": 1000,  # Large quantity
            "user_id": "test_user"
        }
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "insufficient" in data["detail"].lower()