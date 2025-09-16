"""
Test advanced features and edge cases for the inventory management system.

Tests advanced inventory operations, supplier features, location features,
transaction history, filtering, and edge cases not covered in basic tests.
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
import uuid
from datetime import datetime, timedelta


class TestAdvancedInventoryOperations:
    """Test advanced inventory management operations."""
    
    def test_direct_inventory_update(self, client: TestClient):
        """Test direct inventory quantity updates via PUT."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, product
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Inventory Update Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Inventory Update Location {unique_id}",
            "code": f"IU{unique_id[:6].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"IU-{unique_id}",
            "name": f"Inventory Update Product {unique_id}",
            "unit_cost": 25.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Test direct inventory update
        update_data = {
            "quantity_on_hand": 100,
            "reserved_quantity": 20
        }
        
        update_response = client.put(
            f"/api/v1/inventory/{product_id}/{location_id}",
            json=update_data
        )
        assert update_response.status_code == 200
        
        updated_inventory = update_response.json()
        assert updated_inventory["quantity_on_hand"] == 100
        assert updated_inventory["reserved_quantity"] == 20
        assert updated_inventory["available_quantity"] == 80  # 100 - 20
        
        # Verify the update persisted
        get_response = client.get(f"/api/v1/inventory/{product_id}/{location_id}")
        assert get_response.status_code == 200
        retrieved_inventory = get_response.json()
        assert retrieved_inventory["quantity_on_hand"] == 100
        assert retrieved_inventory["reserved_quantity"] == 20
    
    def test_location_inventory_with_details(self, client: TestClient):
        """Test location inventory endpoint with product details."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, multiple products
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Location Inventory Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Location Inventory Location {unique_id}",
            "code": f"LI{unique_id[:6].upper()}"
        })
        location_id = location_response.json()["id"]
        
        # Create multiple products with inventory
        products = []
        for i in range(3):
            product_response = client.post("/api/v1/products/", json={
                "sku": f"LI-{unique_id}-{i}",
                "name": f"Location Product {unique_id} {i}",
                "unit_cost": 10.00 + i * 5,  # Different costs
                "supplier_id": supplier_id
            })
            product_id = product_response.json()["id"]
            products.append(product_id)
            
            # Add inventory via receipt
            client.post("/api/v1/transactions/receipt", params={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": 50 + i * 10,  # Different quantities
                "user_id": "location_test_user"
            })
        
        # Test location inventory endpoint
        location_inventory_response = client.get(f"/api/v1/inventory/location/{location_id}")
        assert location_inventory_response.status_code == 200
        
        location_inventory = location_inventory_response.json()
        assert len(location_inventory) == 3  # Should have all 3 products
        
        # Verify inventory details include product information and value calculations
        for inv in location_inventory:
            assert "product_sku" in inv
            assert "product_name" in inv
            assert "unit_cost" in inv
            assert "total_value" in inv
            assert inv["quantity_on_hand"] > 0
            assert inv["total_value"] == inv["unit_cost"] * inv["quantity_on_hand"]
    
    def test_inventory_summary_statistics(self, client: TestClient):
        """Test inventory summary endpoint with comprehensive statistics."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, products with varied inventory
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Summary Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Summary Location {unique_id}",
            "code": f"SUM{unique_id[:6].upper()}"
        })
        location_id = location_response.json()["id"]
        
        # Create products with different inventory levels and costs
        total_expected_value = 0
        total_expected_quantity = 0
        products_with_stock = 0
        
        for i in range(4):
            unit_cost = 15.00 + i * 10
            quantity = 25 + i * 15
            
            product_response = client.post("/api/v1/products/", json={
                "sku": f"SUM-{unique_id}-{i}",
                "name": f"Summary Product {unique_id} {i}",
                "unit_cost": unit_cost,
                "supplier_id": supplier_id,
                "reorder_point": 10  # Some will be low stock
            })
            product_id = product_response.json()["id"]
            
            if i < 3:  # Only add inventory to first 3 products
                client.post("/api/v1/transactions/receipt", params={
                    "product_id": product_id,
                    "location_id": location_id,
                    "quantity": quantity,
                    "user_id": "summary_test_user"
                })
                
                # Reserve some inventory on first product
                if i == 0:
                    client.post(f"/api/v1/inventory/{product_id}/{location_id}/reserve", 
                               params={"quantity": 10})
                
                total_expected_value += unit_cost * quantity
                total_expected_quantity += quantity
                products_with_stock += 1
        
        # Get inventory summary
        summary_response = client.get("/api/v1/inventory/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        
        # Verify summary statistics (values should be at least what we created)
        assert summary["total_products_with_stock"] >= products_with_stock
        assert summary["total_quantity_on_hand"] >= total_expected_quantity
        assert summary["total_reserved_quantity"] >= 10  # At least first product reserved
        assert summary["total_available_quantity"] >= total_expected_quantity - 10
        assert summary["total_inventory_value"] >= total_expected_value
        assert "low_stock_products" in summary  # Should be calculated


class TestAdvancedSupplierFeatures:
    """Test advanced supplier management features."""
    
    def test_supplier_statistics(self, client: TestClient):
        """Test supplier statistics endpoint."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create suppliers with different characteristics
        suppliers = []
        for i in range(3):
            supplier_response = client.post("/api/v1/suppliers/", json={
                "name": f"Stats Supplier {unique_id} {i}",
                "lead_time_days": 5 + i,
                "performance_rating": 3.0 + i,
                "is_active": i < 2  # Make one inactive
            })
            suppliers.append(supplier_response.json()["id"])
        
        # Get statistics
        stats_response = client.get("/api/v1/suppliers/statistics")
        assert stats_response.status_code == 200
        
        stats = stats_response.json()
        assert "total_suppliers" in stats
        assert "active_suppliers" in stats
        assert "inactive_suppliers" in stats
        assert "average_lead_time_days" in stats
        assert "average_performance_rating" in stats
        
        # Verify counts
        assert stats["total_suppliers"] >= 3
        assert stats["active_suppliers"] >= 2
        assert stats["inactive_suppliers"] >= 1
    
    def test_supplier_products_relationship(self, client: TestClient):
        """Test getting products for a specific supplier."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create supplier
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Product Supplier {unique_id}",
            "lead_time_days": 7
        })
        supplier_id = supplier_response.json()["id"]
        
        # Create products for this supplier
        expected_products = []
        for i in range(3):
            product_response = client.post("/api/v1/products/", json={
                "sku": f"SP-{unique_id}-{i}",
                "name": f"Supplier Product {unique_id} {i}",
                "unit_cost": 20.00 + i * 5,
                "supplier_id": supplier_id
            })
            expected_products.append(product_response.json()["id"])
        
        # Get supplier products
        products_response = client.get(f"/api/v1/suppliers/{supplier_id}/products")
        assert products_response.status_code == 200
        
        supplier_products = products_response.json()
        assert len(supplier_products) == 3
        
        # Verify all products belong to this supplier
        for product in supplier_products:
            assert product["supplier_id"] == supplier_id
            assert product["id"] in expected_products
    
    def test_supplier_performance_management(self, client: TestClient):
        """Test supplier performance rating management."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create supplier
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Performance Supplier {unique_id}",
            "lead_time_days": 5,
            "performance_rating": 3.5
        })
        supplier_id = supplier_response.json()["id"]
        
        # Get initial performance (from supplier details since performance endpoint returns metrics)
        supplier_response = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert supplier_response.status_code == 200
        initial_performance = supplier_response.json()
        assert initial_performance["performance_rating"] == 3.5
        
        # Update performance rating
        update_response = client.put(
            f"/api/v1/suppliers/{supplier_id}/performance",
            params={"new_rating": 4.2}
        )
        assert update_response.status_code == 200
        
        # Verify performance was updated (check supplier details)
        updated_supplier = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert updated_supplier.status_code == 200
        updated_data = updated_supplier.json()
        assert abs(updated_data["performance_rating"] - 4.2) < 0.01
        
        # Verify it's reflected in supplier details too
        supplier_details = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert abs(supplier_details.json()["performance_rating"] - 4.2) < 0.01
    
    def test_suppliers_needing_review(self, client: TestClient):
        """Test endpoint for suppliers needing performance review."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create suppliers with different performance ratings
        low_rating_supplier = client.post("/api/v1/suppliers/", json={
            "name": f"Low Rating Supplier {unique_id}",
            "lead_time_days": 5,
            "performance_rating": 2.0  # Low rating, needs review
        })
        
        high_rating_supplier = client.post("/api/v1/suppliers/", json={
            "name": f"High Rating Supplier {unique_id}",
            "lead_time_days": 5,
            "performance_rating": 4.5  # High rating, no review needed
        })
        
        # Get suppliers needing review (typically rating < 3.0)
        review_response = client.get("/api/v1/suppliers/review-needed", params={"size": 1000})
        assert review_response.status_code == 200
        
        suppliers_needing_review = review_response.json()
        
        # Debug: Check what ratings the suppliers actually have
        low_rating_id = low_rating_supplier.json()["id"]
        high_rating_id = high_rating_supplier.json()["id"]
        
        low_supplier_details = client.get(f"/api/v1/suppliers/{low_rating_id}").json()
        high_supplier_details = client.get(f"/api/v1/suppliers/{high_rating_id}").json()
        
        print(f"Low rating supplier ({low_rating_id}): rating = {low_supplier_details.get('performance_rating')}")
        print(f"High rating supplier ({high_rating_id}): rating = {high_supplier_details.get('performance_rating')}")
        
        # Find our test suppliers in the results
        low_rating_found = any(
            s["id"] == low_rating_id 
            for s in suppliers_needing_review
        )
        high_rating_found = any(
            s["id"] == high_rating_id 
            for s in suppliers_needing_review
        )
        
        # Debug: Print suppliers that need review
        review_ids_and_ratings = [(s["id"], s.get("performance_rating")) for s in suppliers_needing_review]
        print(f"Suppliers needing review: {review_ids_and_ratings}")
        
        assert low_rating_found, f"Low rating supplier {low_rating_id} (rating: {low_supplier_details.get('performance_rating')}) should need review"
        assert not high_rating_found, f"High rating supplier {high_rating_id} (rating: {high_supplier_details.get('performance_rating')}) should not need review"


class TestAdvancedLocationFeatures:
    """Test advanced location management features."""
    
    def test_location_statistics(self, client: TestClient):
        """Test location statistics endpoint."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create locations with different types
        locations = []
        for i, warehouse_type in enumerate(["Distribution", "Retail", "Warehouse"]):
            location_response = client.post("/api/v1/locations/", json={
                "name": f"Stats Location {unique_id} {i}",
                "code": f"SL{unique_id[:5].upper()}{i}",
                "warehouse_type": warehouse_type,
                "is_active": i < 2  # Make one inactive
            })
            locations.append(location_response.json()["id"])
        
        # Get location statistics
        stats_response = client.get("/api/v1/locations/statistics")
        assert stats_response.status_code == 200
        
        stats = stats_response.json()
        assert "total_locations" in stats
        assert "active_locations" in stats
        assert "inactive_locations" in stats
        assert "warehouse_types" in stats
        
        # Verify counts
        assert stats["total_locations"] >= 3
        assert stats["active_locations"] >= 2
        assert stats["inactive_locations"] >= 1
        assert len(stats["warehouse_types"]) >= 2  # At least Distribution and Retail
    
    def test_warehouse_types_endpoint(self, client: TestClient):
        """Test getting available warehouse types."""
        response = client.get("/api/v1/locations/warehouse-types")
        assert response.status_code == 200
        
        warehouse_types = response.json()
        assert isinstance(warehouse_types, list)
        assert len(warehouse_types) > 0
        
        # Should include common warehouse types
        common_types = {"Distribution", "Warehouse", "Retail", "Manufacturing"}
        found_types = set(warehouse_types)
        assert len(common_types & found_types) > 0  # At least some overlap
    
    def test_location_activity_tracking(self, client: TestClient):
        """Test location activity and transaction history."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, product
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Activity Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Activity Location {unique_id}",
            "code": f"ACT{unique_id[:5].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"ACT-{unique_id}",
            "name": f"Activity Product {unique_id}",
            "unit_cost": 30.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Create multiple transactions at this location
        transactions_created = []
        
        # Receipt
        receipt_response = client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 100,
            "reference_number": f"PO-{unique_id}",
            "user_id": "activity_user"
        })
        transactions_created.append(receipt_response.json()["id"])
        
        # Shipment
        shipment_response = client.post("/api/v1/transactions/shipment", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 30,
            "reference_number": f"SO-{unique_id}",
            "user_id": "activity_user"
        })
        transactions_created.append(shipment_response.json()["id"])
        
        # Adjustment
        adjustment_response = client.post("/api/v1/transactions/adjustment", params={
            "product_id": product_id,
            "location_id": location_id,
            "adjustment_quantity": -5,
            "reason": "Damaged goods",
            "user_id": "activity_user"
        })
        transactions_created.append(adjustment_response.json()["id"])
        
        # Get location activity
        activity_response = client.get(f"/api/v1/locations/{location_id}/activity")
        assert activity_response.status_code == 200
        
        activity = activity_response.json()
        assert "total_transactions" in activity
        assert "recent_transactions" in activity
        assert "transaction_types" in activity
        
        # Verify activity tracking
        assert activity["total_transactions"] >= 3
        assert len(activity["recent_transactions"]) >= 3
        
        # Verify transaction types breakdown
        transaction_types = activity["transaction_types"]
        assert "IN" in transaction_types
        assert "OUT" in transaction_types
        assert "ADJUSTMENT" in transaction_types
    
    def test_empty_locations_detection(self, client: TestClient):
        """Test detection of locations with no inventory."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create empty location
        empty_location_response = client.post("/api/v1/locations/", json={
            "name": f"Empty Location {unique_id}",
            "code": f"EMP{unique_id[:5].upper()}"
        })
        empty_location_id = empty_location_response.json()["id"]
        
        # Create location with inventory
        active_location_response = client.post("/api/v1/locations/", json={
            "name": f"Active Location {unique_id}",
            "code": f"ACT{unique_id[:5].upper()}"
        })
        active_location_id = active_location_response.json()["id"]
        
        # Add inventory to active location
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Empty Test Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"EMP-{unique_id}",
            "name": f"Empty Test Product {unique_id}",
            "unit_cost": 25.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Add inventory only to active location
        client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": active_location_id,
            "quantity": 50,
            "user_id": "empty_test_user"
        })
        
        # Get empty locations
        empty_response = client.get("/api/v1/locations/empty")
        assert empty_response.status_code == 200
        
        empty_locations = empty_response.json()
        empty_location_ids = [loc["id"] for loc in empty_locations]
        
        # Verify empty location is detected and active location is not
        assert empty_location_id in empty_location_ids
        assert active_location_id not in empty_location_ids


class TestTransactionHistoryAndFiltering:
    """Test transaction history and advanced filtering capabilities."""
    
    def test_product_transaction_history(self, client: TestClient):
        """Test getting complete transaction history for a product."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, product
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"History Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"History Location {unique_id}",
            "code": f"HIST{unique_id[:4].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"HIST-{unique_id}",
            "name": f"History Product {unique_id}",
            "unit_cost": 40.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Create diverse transaction history
        expected_transactions = []
        
        # Receipt
        receipt = client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 200,
            "reference_number": f"HIST-PO-{unique_id}",
            "user_id": "history_user"
        })
        expected_transactions.append(receipt.json()["id"])
        
        # Multiple shipments
        for i in range(3):
            shipment = client.post("/api/v1/transactions/shipment", params={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": 25 + i * 5,
                "reference_number": f"HIST-SO-{unique_id}-{i}",
                "user_id": "history_user"
            })
            expected_transactions.append(shipment.json()["id"])
        
        # Adjustment
        adjustment = client.post("/api/v1/transactions/adjustment", params={
            "product_id": product_id,
            "location_id": location_id,
            "adjustment_quantity": -10,
            "reason": f"History test adjustment {unique_id}",
            "user_id": "history_user"
        })
        expected_transactions.append(adjustment.json()["id"])
        
        # Get product transaction history
        history_response = client.get(f"/api/v1/transactions/product/{product_id}/history")
        assert history_response.status_code == 200
        
        transaction_history = history_response.json()
        assert len(transaction_history) >= len(expected_transactions)
        
        # Verify all our transactions are in the history
        history_ids = [t["id"] for t in transaction_history]
        for expected_id in expected_transactions:
            assert expected_id in history_ids
        
        # Verify transactions are ordered by most recent first
        timestamps = [t["created_at"] for t in transaction_history]
        sorted_timestamps = sorted(timestamps, reverse=True)
        assert timestamps == sorted_timestamps
    
    def test_transaction_filtering_capabilities(self, client: TestClient):
        """Test comprehensive transaction filtering options."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, locations, products
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Filter Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        # Create two locations
        location1_response = client.post("/api/v1/locations/", json={
            "name": f"Filter Location 1 {unique_id}",
            "code": f"FL1{unique_id[:5].upper()}"
        })
        location1_id = location1_response.json()["id"]
        
        location2_response = client.post("/api/v1/locations/", json={
            "name": f"Filter Location 2 {unique_id}",
            "code": f"FL2{unique_id[:5].upper()}"
        })
        location2_id = location2_response.json()["id"]
        
        # Create two products
        product1_response = client.post("/api/v1/products/", json={
            "sku": f"FILT1-{unique_id}",
            "name": f"Filter Product 1 {unique_id}",
            "unit_cost": 50.00,
            "supplier_id": supplier_id
        })
        product1_id = product1_response.json()["id"]
        
        product2_response = client.post("/api/v1/products/", json={
            "sku": f"FILT2-{unique_id}",
            "name": f"Filter Product 2 {unique_id}",
            "unit_cost": 75.00,
            "supplier_id": supplier_id
        })
        product2_id = product2_response.json()["id"]
        
        # Create transactions with different characteristics
        transactions = []
        
        # Product 1, Location 1 - Receipt
        t1 = client.post("/api/v1/transactions/receipt", params={
            "product_id": product1_id,
            "location_id": location1_id,
            "quantity": 100,
            "reference_number": f"REF-A-{unique_id}",
            "user_id": "filter_user_a"
        })
        transactions.append(("receipt", t1.json()))
        
        # Add some inventory to location2 first so we can ship from it
        client.post("/api/v1/transactions/receipt", params={
            "product_id": product1_id,
            "location_id": location2_id,
            "quantity": 50,
            "user_id": "filter_setup_user"
        })
        
        # Product 1, Location 2 - Shipment
        t2 = client.post("/api/v1/transactions/shipment", params={
            "product_id": product1_id,
            "location_id": location2_id,
            "quantity": 30,
            "reference_number": f"REF-B-{unique_id}",
            "user_id": "filter_user_b"
        })
        assert t2.status_code == 200, f"Shipment failed: {t2.text}"
        transactions.append(("shipment", t2.json()))
        
        # Product 2, Location 1 - Adjustment
        t3 = client.post("/api/v1/transactions/adjustment", params={
            "product_id": product2_id,
            "location_id": location1_id,
            "adjustment_quantity": 15,
            "reason": f"Filter test adjustment {unique_id}",
            "user_id": "filter_user_c"
        })
        transactions.append(("adjustment", t3.json()))
        
        # Test filtering by product_id
        product1_filter = client.get("/api/v1/transactions/", params={"product_id": product1_id})
        assert product1_filter.status_code == 200
        product1_transactions = product1_filter.json()
        product1_ids = [t["id"] for t in product1_transactions]
        assert t1.json()["id"] in product1_ids
        assert t2.json()["id"] in product1_ids
        assert t3.json()["id"] not in product1_ids
        
        # Test filtering by location_id
        location1_filter = client.get("/api/v1/transactions/", params={"location_id": location1_id})
        assert location1_filter.status_code == 200
        location1_transactions = location1_filter.json()
        location1_ids = [t["id"] for t in location1_transactions]
        assert t1.json()["id"] in location1_ids
        assert t3.json()["id"] in location1_ids
        assert t2.json()["id"] not in location1_ids
        
        # Test filtering by transaction_type
        adjustment_filter = client.get("/api/v1/transactions/", params={"transaction_type": "ADJUSTMENT"})
        assert adjustment_filter.status_code == 200
        adjustment_transactions = adjustment_filter.json()
        adjustment_ids = [t["id"] for t in adjustment_transactions]
        assert t3.json()["id"] in adjustment_ids
        # t1 and t2 might not be in results depending on their actual transaction types
        
        # Test filtering by reference_number  
        ref_filter = client.get("/api/v1/transactions/", params={"reference_number": f"REF-A-{unique_id}"})
        assert ref_filter.status_code == 200
        ref_transactions = ref_filter.json()
        ref_ids = [t["id"] for t in ref_transactions]
        assert t1.json()["id"] in ref_ids
        assert len([t for t in ref_transactions if t["reference_number"] == f"REF-A-{unique_id}"]) >= 1
        
        # Test pagination
        paginated = client.get("/api/v1/transactions/", params={"page": 1, "size": 2})
        assert paginated.status_code == 200
        paginated_transactions = paginated.json()
        assert len(paginated_transactions) <= 2
    
    def test_transaction_summary_with_filtering(self, client: TestClient):
        """Test transaction summary statistics with date filtering."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, product
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Summary Filter Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Summary Filter Location {unique_id}",
            "code": f"SF{unique_id[:6].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"SF-{unique_id}",
            "name": f"Summary Filter Product {unique_id}",
            "unit_cost": 60.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Create transactions of different types
        # Receipt - IN transaction
        client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 150,
            "user_id": "summary_user"
        })
        
        # Shipments - OUT transactions  
        client.post("/api/v1/transactions/shipment", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 40,
            "user_id": "summary_user"
        })
        
        client.post("/api/v1/transactions/shipment", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 25,
            "user_id": "summary_user"
        })
        
        # Adjustment transaction
        client.post("/api/v1/transactions/adjustment", params={
            "product_id": product_id,
            "location_id": location_id,
            "adjustment_quantity": -5,
            "reason": "Summary test adjustment",
            "user_id": "summary_user"
        })
        
        # Get overall transaction summary
        summary_response = client.get("/api/v1/transactions/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        
        # Verify summary structure and basic statistics
        assert "total_transactions" in summary
        assert "in_transactions" in summary
        assert "out_transactions" in summary
        assert "transfer_transactions" in summary
        assert "adjustment_transactions" in summary
        assert "total_quantity_in" in summary
        assert "total_quantity_out" in summary
        
        # Verify our transactions are reflected in the summary
        assert summary["total_transactions"] >= 4
        assert summary["in_transactions"] >= 1  # Receipt
        assert summary["out_transactions"] >= 2  # Shipments
        assert summary["adjustment_transactions"] >= 1  # Adjustment
        assert summary["total_quantity_in"] >= 150  # From receipt
        assert summary["total_quantity_out"] >= 65   # From shipments (40 + 25)
        
        # Test filtered summary by product
        product_summary = client.get("/api/v1/transactions/summary", params={"product_id": product_id})
        assert product_summary.status_code == 200
        
        product_summary_data = product_summary.json()
        # Product-filtered summary should have fewer or equal transactions
        assert product_summary_data["total_transactions"] <= summary["total_transactions"]


class TestEdgeCasesAndBusinessRules:
    """Test edge cases and complex business rule scenarios."""
    
    def test_concurrent_reservation_attempts(self, client: TestClient):
        """Test handling of concurrent inventory reservations."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: supplier, location, product with limited inventory
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Concurrent Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location_response = client.post("/api/v1/locations/", json={
            "name": f"Concurrent Location {unique_id}",
            "code": f"CON{unique_id[:5].upper()}"
        })
        location_id = location_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"CON-{unique_id}",
            "name": f"Concurrent Product {unique_id}",
            "unit_cost": 35.00,
            "supplier_id": supplier_id
        })
        product_id = product_response.json()["id"]
        
        # Add limited inventory
        client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": location_id,
            "quantity": 50,
            "user_id": "concurrent_user"
        })
        
        # First reservation should succeed
        reserve1_response = client.post(
            f"/api/v1/inventory/{product_id}/{location_id}/reserve",
            params={"quantity": 30}
        )
        assert reserve1_response.status_code == 200
        
        # Second reservation for remaining inventory should succeed
        reserve2_response = client.post(
            f"/api/v1/inventory/{product_id}/{location_id}/reserve",
            params={"quantity": 20}
        )
        assert reserve2_response.status_code == 200
        
        # Third reservation should fail (no available inventory)
        reserve3_response = client.post(
            f"/api/v1/inventory/{product_id}/{location_id}/reserve",
            params={"quantity": 1}
        )
        assert reserve3_response.status_code == 400
        assert "cannot reserve" in reserve3_response.json()["detail"].lower()
        
        # Verify total reservations
        inventory_check = client.get(f"/api/v1/inventory/{product_id}/{location_id}")
        inventory = inventory_check.json()
        assert inventory["reserved_quantity"] == 50  # 30 + 20
        assert inventory["available_quantity"] == 0   # 50 - 50
    
    def test_complex_filtering_combinations(self, client: TestClient):
        """Test complex combinations of filters and edge cases."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Test pagination edge cases
        # Very large page size
        large_page = client.get("/api/v1/suppliers/", params={"size": 1000})
        assert large_page.status_code == 200
        
        # Invalid page numbers should be handled gracefully
        invalid_page = client.get("/api/v1/suppliers/", params={"page": 0})
        # Should either return 422 or handle gracefully
        assert invalid_page.status_code in [422, 200]
        
        # Combine multiple filters
        multi_filter = client.get("/api/v1/suppliers/", params={
            "is_active": True,
            "min_rating": 3.0,
            "size": 10
        })
        assert multi_filter.status_code == 200
        
        suppliers = multi_filter.json()
        # All returned suppliers should meet the criteria
        for supplier in suppliers:
            assert supplier["is_active"] == True
            assert supplier["performance_rating"] >= 3.0
    
    def test_data_consistency_across_operations(self, client: TestClient):
        """Test data consistency across complex operation sequences."""
        unique_id = str(uuid.uuid4())[:8]
        
        # Create a complete scenario with supplier, locations, products
        supplier_response = client.post("/api/v1/suppliers/", json={
            "name": f"Consistency Supplier {unique_id}",
            "lead_time_days": 5
        })
        supplier_id = supplier_response.json()["id"]
        
        location1_response = client.post("/api/v1/locations/", json={
            "name": f"Consistency Location 1 {unique_id}",
            "code": f"CS1{unique_id[:5].upper()}"
        })
        location1_id = location1_response.json()["id"]
        
        location2_response = client.post("/api/v1/locations/", json={
            "name": f"Consistency Location 2 {unique_id}",
            "code": f"CS2{unique_id[:5].upper()}"
        })
        location2_id = location2_response.json()["id"]
        
        product_response = client.post("/api/v1/products/", json={
            "sku": f"CONS-{unique_id}",
            "name": f"Consistency Product {unique_id}",
            "unit_cost": 45.00,
            "supplier_id": supplier_id,
            "reorder_point": 25
        })
        product_id = product_response.json()["id"]
        
        # Complex operation sequence
        initial_quantity = 100
        
        # 1. Add initial inventory
        client.post("/api/v1/transactions/receipt", params={
            "product_id": product_id,
            "location_id": location1_id,
            "quantity": initial_quantity,
            "user_id": "consistency_user"
        })
        
        # 2. Reserve some inventory
        reservation_qty = 20
        client.post(f"/api/v1/inventory/{product_id}/{location1_id}/reserve",
                   params={"quantity": reservation_qty})
        
        # 3. Ship some inventory
        shipment_qty = 30
        client.post("/api/v1/transactions/shipment", params={
            "product_id": product_id,
            "location_id": location1_id,
            "quantity": shipment_qty,
            "user_id": "consistency_user"
        })
        
        # 4. Transfer some inventory to second location
        transfer_qty = 25
        client.post("/api/v1/transactions/transfer", params={
            "product_id": product_id,
            "from_location_id": location1_id,
            "to_location_id": location2_id,
            "quantity": transfer_qty,
            "user_id": "consistency_user"
        })
        
        # 5. Make an adjustment
        adjustment_qty = -3
        client.post("/api/v1/transactions/adjustment", params={
            "product_id": product_id,
            "location_id": location1_id,
            "adjustment_quantity": adjustment_qty,
            "reason": "Consistency test damage",
            "user_id": "consistency_user"
        })
        
        # Verify final state consistency
        # Location 1 should have: 100 - 30 (shipped) - 25 (transferred) - 3 (adjusted) = 42
        # Plus 20 reserved = 62 total on hand, 42 available
        location1_inventory = client.get(f"/api/v1/inventory/{product_id}/{location1_id}").json()
        expected_location1_total = initial_quantity - shipment_qty - transfer_qty + adjustment_qty
        assert location1_inventory["quantity_on_hand"] == expected_location1_total  # 42
        assert location1_inventory["reserved_quantity"] == reservation_qty  # 20
        assert location1_inventory["available_quantity"] == expected_location1_total - reservation_qty  # 22
        
        # Location 2 should have the transferred quantity
        location2_inventory = client.get(f"/api/v1/inventory/{product_id}/{location2_id}").json()
        assert location2_inventory["quantity_on_hand"] == transfer_qty  # 25
        assert location2_inventory["reserved_quantity"] == 0
        assert location2_inventory["available_quantity"] == transfer_qty  # 25
        
        # Total available across both locations
        total_available = (expected_location1_total - reservation_qty) + transfer_qty  # 22 + 25 = 47
        
        # Check if product appears in low stock (47 > 25 reorder point, so should not appear)
        low_stock_response = client.get("/api/v1/inventory/alerts/low-stock")
        low_stock_products = low_stock_response.json()
        low_stock_ids = [alert["product_id"] for alert in low_stock_products]
        assert product_id not in low_stock_ids, f"Product should not be low stock with {total_available} available vs {25} reorder point"
        
        # Verify transaction history reflects all operations
        history = client.get(f"/api/v1/transactions/product/{product_id}/history").json()
        assert len(history) >= 5  # Receipt, shipment, 2 transfers (out & in), adjustment
        
        # Verify transaction types in history
        transaction_types = [t["transaction_type"] for t in history]
        assert "IN" in transaction_types
        assert "OUT" in transaction_types
        assert "TRANSFER" in transaction_types
        assert "ADJUSTMENT" in transaction_types