"""
Comprehensive inventory management API tests.

Tests all core CRUD operations, business logic, and error handling
for the AI4SupplyChain backend inventory system.
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
import uuid


class TestSupplierAPI:
    """Test supplier management endpoints."""
    
    def test_supplier_crud_lifecycle(self, client: TestClient):
        """Test complete supplier CRUD operations."""
        unique_id = str(uuid.uuid4())[:8]
        
        # CREATE
        supplier_data = {
            "name": f"Test Supplier {unique_id}",
            "contact_person": "John Doe",
            "email": f"john{unique_id}@testsupplier.com",
            "lead_time_days": 5,
            "payment_terms": "Net 30",
            "minimum_order_qty": 10
        }
        
        create_response = client.post("/api/v1/suppliers/", json=supplier_data)
        assert create_response.status_code == 200
        
        created_supplier = create_response.json()
        assert created_supplier["name"] == supplier_data["name"]
        assert created_supplier["is_active"] == True
        supplier_id = created_supplier["id"]
        
        # READ
        get_response = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == supplier_data["name"]
        
        # UPDATE
        update_data = {"lead_time_days": 10, "performance_rating": 4.5}
        update_response = client.put(f"/api/v1/suppliers/{supplier_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["lead_time_days"] == 10
        
        # LIST (verify our supplier appears with increased page size to handle all test data)
        list_response = client.get("/api/v1/suppliers/", params={"size": 1000})
        assert list_response.status_code == 200
        suppliers = list_response.json()
        # Check the supplier was created and exists before deletion
        our_supplier = next((s for s in suppliers if s["id"] == supplier_id), None)
        assert our_supplier is not None, f"Supplier {supplier_id} not found in list of {len(suppliers)} suppliers"
        assert our_supplier["name"] == supplier_data["name"]
        
        # DELETE (soft delete)
        delete_response = client.delete(f"/api/v1/suppliers/{supplier_id}")
        assert delete_response.status_code == 200
        
        # Verify soft delete
        final_get = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert final_get.status_code == 200
        assert final_get.json()["is_active"] == False
    
    def test_supplier_validation_errors(self, client: TestClient):
        """Test supplier validation and error handling."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Test duplicate name error
        supplier_data = {"name": f"Duplicate Supplier {unique_id}", "lead_time_days": 5}
        
        response1 = client.post("/api/v1/suppliers/", json=supplier_data)
        assert response1.status_code == 200
        
        response2 = client.post("/api/v1/suppliers/", json=supplier_data)
        assert response2.status_code == 409
        
        # Test 404 for non-existent supplier
        response = client.get("/api/v1/suppliers/99999")
        assert response.status_code == 404


class TestLocationAPI:
    """Test location management endpoints."""
    
    def test_location_crud_lifecycle(self, client: TestClient):
        """Test complete location CRUD operations."""
        unique_id = str(uuid.uuid4())[:8]
        
        # CREATE
        location_data = {
            "name": f"Test Location {unique_id}",
            "code": f"TL{unique_id[:6].upper()}",
            "address": "123 Test Ave",
            "warehouse_type": "Distribution"
        }
        
        create_response = client.post("/api/v1/locations/", json=location_data)
        assert create_response.status_code == 200
        
        created_location = create_response.json()
        assert created_location["name"] == location_data["name"]
        assert created_location["code"] == location_data["code"]
        location_id = created_location["id"]
        
        # READ
        get_response = client.get(f"/api/v1/locations/{location_id}")
        assert get_response.status_code == 200
        
        # UPDATE
        update_data = {"warehouse_type": "Retail", "address": "Updated Address"}
        update_response = client.put(f"/api/v1/locations/{location_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["warehouse_type"] == "Retail"
        
        # DELETE
        delete_response = client.delete(f"/api/v1/locations/{location_id}")
        assert delete_response.status_code == 200


class TestProductAPI:
    """Test product management endpoints."""
    
    def test_product_with_supplier_relationship(self, client: TestClient):
        """Test product CRUD with supplier relationships."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create supplier first
        supplier_data = {"name": f"Product Supplier {unique_id}", "lead_time_days": 5}
        supplier_response = client.post("/api/v1/suppliers/", json=supplier_data)
        supplier_id = supplier_response.json()["id"]
        
        # CREATE product
        product_data = {
            "sku": f"PROD-{unique_id}",
            "name": f"Test Product {unique_id}",
            "description": "A comprehensive test product",
            "category": "Electronics",
            "unit_cost": 25.50,
            "unit_price": 45.00,
            "reorder_point": 10,
            "reorder_quantity": 50,
            "supplier_id": supplier_id
        }
        
        create_response = client.post("/api/v1/products/", json=product_data)
        assert create_response.status_code == 200
        
        created_product = create_response.json()
        assert created_product["sku"] == product_data["sku"]
        assert created_product["supplier_id"] == supplier_id
        product_id = created_product["id"]
        
        # READ by ID
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 200
        
        # READ by SKU
        sku_response = client.get(f"/api/v1/products/sku/{product_data['sku']}")
        assert sku_response.status_code == 200
        assert sku_response.json()["id"] == product_id
        
        # UPDATE
        update_data = {"unit_price": 50.00, "description": "Updated description"}
        update_response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert update_response.status_code == 200
        assert float(update_response.json()["unit_price"]) == 50.00


class TestInventoryTransactionAPI:
    """Test inventory and transaction management."""
    
    def test_complete_inventory_workflow(self, client: TestClient):
        """Test end-to-end inventory management workflow."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: Create supplier, location, and product
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Inv Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Inv Location {unique_id}",
            "code": f"IL{unique_id[:6].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"INV-{unique_id}",
            "name": f"Inventory Product {unique_id}",
            "unit_cost": 20.00,
            "supplier_id": supplier_id,
            "reorder_point": 5
        })
        product_id = product_response.json()["id"]
        
        # Test 1: STOCK RECEIPT
        receipt_response = client.post(
            "/api/v1/transactions/receipt",
            params={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": 100,
                "reference_number": f"PO-{unique_id}",
                "user_id": "test_user"
            }
        )
        assert receipt_response.status_code == 200
        assert receipt_response.json()["quantity"] == 100
        
        # Verify inventory updated
        inventory = client.get("/api/v1/inventory/").json()
        our_inventory = next(
            inv for inv in inventory 
            if inv["product_id"] == product_id and inv["location_id"] == location_id
        )
        assert our_inventory["quantity_on_hand"] == 100
        
        # Test 2: INVENTORY RESERVATIONS
        reserve_response = client.post(
            f"/api/v1/inventory/{product_id}/{location_id}/reserve",
            params={"quantity": 20}
        )
        assert reserve_response.status_code == 200
        
        # Verify reservation
        reserved_inventory = client.get(f"/api/v1/inventory/{product_id}/{location_id}").json()
        assert reserved_inventory["reserved_quantity"] == 20
        assert reserved_inventory["available_quantity"] == 80
        
        # Test 3: STOCK SHIPMENT
        shipment_response = client.post(
            "/api/v1/transactions/shipment",
            params={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": 30,
                "reference_number": f"DO-{unique_id}",
                "user_id": "test_user"
            }
        )
        assert shipment_response.status_code == 200
        assert shipment_response.json()["quantity"] == -30
        
        # Verify inventory after shipment
        post_shipment = client.get("/api/v1/inventory/").json()
        our_post_shipment = next(
            inv for inv in post_shipment 
            if inv["product_id"] == product_id and inv["location_id"] == location_id
        )
        assert our_post_shipment["quantity_on_hand"] == 70  # 100 - 30
        
        # Test 4: STOCK ADJUSTMENT
        adjustment_response = client.post(
            "/api/v1/transactions/adjustment",
            params={
                "product_id": product_id,
                "location_id": location_id,
                "adjustment_quantity": -5,
                "reason": "Damaged goods",
                "user_id": "test_user"
            }
        )
        assert adjustment_response.status_code == 200
        
        # Verify final inventory state
        final_inventory = client.get("/api/v1/inventory/").json()
        final_state = next(
            inv for inv in final_inventory 
            if inv["product_id"] == product_id and inv["location_id"] == location_id
        )
        assert final_state["quantity_on_hand"] == 65  # 70 - 5
        
        # Test 5: RELEASE RESERVATIONS
        release_response = client.post(
            f"/api/v1/inventory/{product_id}/{location_id}/release",
            params={"quantity": 20}
        )
        assert release_response.status_code == 200
        
        # Test 6: TRANSACTION HISTORY
        transactions = client.get("/api/v1/transactions/").json()
        our_transactions = [t for t in transactions if t["product_id"] == product_id]
        assert len(our_transactions) >= 3  # Receipt, shipment, adjustment
    
    def test_error_handling(self, client: TestClient):
        """Test comprehensive error handling."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup minimal data
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Error Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Error Location {unique_id}",
            "code": f"ERR{unique_id[:5].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"ERR-{unique_id}",
            "name": f"Error Product {unique_id}",
            "unit_cost": 10.0,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Test insufficient stock error
        insufficient_shipment = client.post(
            "/api/v1/transactions/shipment",
            params={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": 50,  # No stock available
                "user_id": "error_user"
            }
        )
        assert insufficient_shipment.status_code == 400
        assert "insufficient" in insufficient_shipment.json()["detail"].lower()
        
        # Test invalid product ID
        invalid_product = client.get("/api/v1/products/99999")
        assert invalid_product.status_code == 404
        
        # Test duplicate SKU error
        duplicate_product = client.post("/api/v1/products/", json={
            "sku": f"ERR-{unique_id}",  # Same SKU as above
            "name": "Duplicate Product",
            "unit_cost": 15.0,
            "supplier_id": supplier_id
        })
        assert duplicate_product.status_code == 409


class TestAPIFeatures:
    """Test additional API features."""
    
    def test_filtering_and_pagination(self, client: TestClient):
        """Test API filtering and pagination."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create multiple suppliers with different ratings
        for i, rating in enumerate([3.0, 4.0, 5.0]):
            supplier_data = {
                "name": f"Filter Supplier {i} {unique_id}",
                "performance_rating": rating,
                "lead_time_days": 5
            }
            response = client.post("/api/v1/suppliers/", json=supplier_data)
            assert response.status_code == 200
        
        # Test filtering by minimum rating
        filtered_response = client.get("/api/v1/suppliers/", params={"min_rating": 4.0})
        assert filtered_response.status_code == 200
        
        # Test pagination
        paginated_response = client.get("/api/v1/suppliers/", params={"page": 1, "size": 2})
        assert paginated_response.status_code == 200
        assert len(paginated_response.json()) <= 2
    
    def test_system_endpoints(self, client: TestClient):
        """Test system information endpoints."""
        # Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # System statistics
        stats_response = client.get("/api/v1/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert "products" in stats_data
        assert "suppliers" in stats_data
        assert "locations" in stats_data
        
        # Transaction summary
        summary_response = client.get("/api/v1/transactions/summary")
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        assert "total_transactions" in summary_data
        assert "in_transactions" in summary_data
        assert "out_transactions" in summary_data