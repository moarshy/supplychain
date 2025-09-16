"""
Test advanced transaction types and error handling.
"""
import uuid
from fastapi.testclient import TestClient


def test_stock_transfer_workflow(client: TestClient):
    """Test stock transfer between locations."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Setup: supplier, 2 locations, product
    supplier_response = client.post("/api/v1/suppliers/", json={
        "name": f"Transfer Supplier {unique_id}",
        "lead_time_days": 5
    })
    supplier_id = supplier_response.json()["id"]
    
    location1_response = client.post("/api/v1/locations/", json={
        "name": f"Source Location {unique_id}",
        "code": f"SRC{unique_id[:5].upper()}"
    })
    location1_id = location1_response.json()["id"]
    
    location2_response = client.post("/api/v1/locations/", json={
        "name": f"Dest Location {unique_id}",
        "code": f"DST{unique_id[:5].upper()}"
    })
    location2_id = location2_response.json()["id"]
    
    product_response = client.post("/api/v1/products/", json={
        "sku": f"TXF-{unique_id}",
        "name": f"Transfer Product {unique_id}",
        "unit_cost": 15.0,
        "supplier_id": supplier_id
    })
    product_id = product_response.json()["id"]
    
    # Add initial stock to source location
    receipt_response = client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": product_id,
            "location_id": location1_id,
            "quantity": 100,
            "user_id": "transfer_user"
        }
    )
    assert receipt_response.status_code == 200
    
    # Verify initial stock
    source_inventory = client.get(f"/api/v1/inventory/{product_id}/{location1_id}").json()
    assert source_inventory["quantity_on_hand"] == 100
    
    dest_inventory = client.get(f"/api/v1/inventory/{product_id}/{location2_id}").json()
    assert dest_inventory["quantity_on_hand"] == 0
    
    # Process stock transfer
    transfer_response = client.post(
        "/api/v1/transactions/transfer",
        params={
            "product_id": product_id,
            "from_location_id": location1_id,
            "to_location_id": location2_id,
            "quantity": 30,
            "reference_number": f"TXF-{unique_id}",
            "user_id": "transfer_user"
        }
    )
    assert transfer_response.status_code == 200
    
    transfer_data = transfer_response.json()
    assert len(transfer_data) == 2  # Should return 2 transactions (OUT and IN)
    
    # Verify transfer transactions
    out_txn = next(t for t in transfer_data if t["quantity"] < 0)
    in_txn = next(t for t in transfer_data if t["quantity"] > 0)
    
    assert out_txn["location_id"] == location1_id
    assert out_txn["quantity"] == -30
    assert in_txn["location_id"] == location2_id
    assert in_txn["quantity"] == 30
    
    # Verify final inventory levels
    final_source = client.get(f"/api/v1/inventory/{product_id}/{location1_id}").json()
    final_dest = client.get(f"/api/v1/inventory/{product_id}/{location2_id}").json()
    
    assert final_source["quantity_on_hand"] == 70  # 100 - 30
    assert final_dest["quantity_on_hand"] == 30    # 0 + 30


def test_error_handling_comprehensive(client: TestClient):
    """Test comprehensive error handling scenarios."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Setup basic entities
    supplier_response = client.post("/api/v1/suppliers/", json={
        "name": f"Error Test Supplier {unique_id}",
        "lead_time_days": 5
    })
    supplier_id = supplier_response.json()["id"]
    
    location_response = client.post("/api/v1/locations/", json={
        "name": f"Error Test Location {unique_id}",
        "code": f"ERR{unique_id[:5].upper()}"
    })
    location_id = location_response.json()["id"]
    
    product_response = client.post("/api/v1/products/", json={
        "sku": f"ERR-{unique_id}",
        "name": f"Error Test Product {unique_id}",
        "unit_cost": 10.0,
        "supplier_id": supplier_id
    })
    product_id = product_response.json()["id"]
    
    # Test 1: Insufficient stock for shipment
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
    
    # Test 2: Invalid product ID  
    invalid_product = client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": 99999,  # Non-existent
            "location_id": location_id,
            "quantity": 10,
            "user_id": "error_user"
        }
    )
    # Should return 404 or 400 depending on implementation
    assert invalid_product.status_code in [400, 404]
    
    # Test 3: Invalid location ID
    invalid_location = client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": product_id,
            "location_id": 99999,  # Non-existent
            "quantity": 10,
            "user_id": "error_user"
        }
    )
    # Should return 404 or 400 depending on implementation  
    assert invalid_location.status_code in [400, 404]
    
    # Test 4: Transfer to same location
    same_location_transfer = client.post(
        "/api/v1/transactions/transfer",
        params={
            "product_id": product_id,
            "from_location_id": location_id,
            "to_location_id": location_id,  # Same as from
            "quantity": 10,
            "user_id": "error_user"
        }
    )
    assert same_location_transfer.status_code == 400
    assert "same" in same_location_transfer.json()["detail"].lower()


def test_inventory_reservations(client: TestClient):
    """Test inventory reservation and release functionality."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Setup
    supplier_response = client.post("/api/v1/suppliers/", json={
        "name": f"Reserve Supplier {unique_id}",
        "lead_time_days": 5
    })
    supplier_id = supplier_response.json()["id"]
    
    location_response = client.post("/api/v1/locations/", json={
        "name": f"Reserve Location {unique_id}",
        "code": f"RES{unique_id[:5].upper()}"
    })
    location_id = location_response.json()["id"]
    
    product_response = client.post("/api/v1/products/", json={
        "sku": f"RES-{unique_id}",
        "name": f"Reserve Product {unique_id}",
        "unit_cost": 20.0,
        "supplier_id": supplier_id
    })
    product_id = product_response.json()["id"]
    
    # Add initial stock
    client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 100,
            "user_id": "reserve_user"
        }
    )
    
    # Test successful reservation
    reserve_response = client.post(
        f"/api/v1/inventory/{product_id}/{location_id}/reserve",
        params={"quantity": 25}
    )
    assert reserve_response.status_code == 200
    
    # Verify reservation
    inventory_after_reserve = client.get(f"/api/v1/inventory/{product_id}/{location_id}").json()
    assert inventory_after_reserve["reserved_quantity"] == 25
    assert inventory_after_reserve["available_quantity"] == 75
    
    # Test over-reservation (should fail)
    over_reserve_response = client.post(
        f"/api/v1/inventory/{product_id}/{location_id}/reserve",
        params={"quantity": 80}  # Only 75 available
    )
    assert over_reserve_response.status_code == 400
    
    # Test release reservation
    release_response = client.post(
        f"/api/v1/inventory/{product_id}/{location_id}/release",
        params={"quantity": 15}
    )
    assert release_response.status_code == 200
    
    # Verify release
    inventory_after_release = client.get(f"/api/v1/inventory/{product_id}/{location_id}").json()
    assert inventory_after_release["reserved_quantity"] == 10  # 25 - 15
    assert inventory_after_release["available_quantity"] == 90  # 100 - 10


def test_low_stock_alerts(client: TestClient):
    """Test low stock alert functionality."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Create supplier and location
    supplier_response = client.post("/api/v1/suppliers/", json={
        "name": f"Alert Supplier {unique_id}",
        "lead_time_days": 5
    })
    supplier_id = supplier_response.json()["id"]
    
    location_response = client.post("/api/v1/locations/", json={
        "name": f"Alert Location {unique_id}",
        "code": f"ALT{unique_id[:5].upper()}"
    })
    location_id = location_response.json()["id"]
    
    # Create product with low reorder point
    product_response = client.post("/api/v1/products/", json={
        "sku": f"ALT-{unique_id}",
        "name": f"Alert Product {unique_id}",
        "unit_cost": 30.0,
        "supplier_id": supplier_id,
        "reorder_point": 20,  # Low reorder point
        "reorder_quantity": 100
    })
    product_id = product_response.json()["id"]
    
    # Add stock above reorder point
    client.post(
        "/api/v1/transactions/receipt",
        params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 50,
            "user_id": "alert_user"
        }
    )
    
    # Check no alerts initially
    alerts_response = client.get("/api/v1/inventory/alerts/low-stock")
    assert alerts_response.status_code == 200, f"Expected 200, got {alerts_response.status_code}: {alerts_response.text}"
    initial_alerts = alerts_response.json()
    our_alerts = [alert for alert in initial_alerts if alert["product_id"] == product_id]
    assert len(our_alerts) == 0  # Should not be in low stock
    
    # Ship stock to bring below reorder point
    client.post(
        "/api/v1/transactions/shipment",
        params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 35,  # 50 - 35 = 15, which is < 20 (reorder point)
            "user_id": "alert_user"
        }
    )
    
    # Check for low stock alerts
    final_alerts_response = client.get("/api/v1/inventory/alerts/low-stock")
    final_alerts = final_alerts_response.json()
    our_final_alerts = [alert for alert in final_alerts if alert["product_id"] == product_id]
    
    assert len(our_final_alerts) > 0  # Should now be in low stock
    alert = our_final_alerts[0]
    assert alert["current_available"] == 15
    assert alert["reorder_point"] == 20
    assert alert["shortage"] == 5  # 20 - 15