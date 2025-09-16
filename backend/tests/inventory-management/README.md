# Inventory Management System Tests

This folder contains comprehensive test coverage for the inventory management system.

## Test Files

### `test_inventory_api.py`
Core CRUD operations and basic API functionality:
- **TestSupplierAPI**: Supplier lifecycle, validation, duplicates  
- **TestLocationAPI**: Location management operations
- **TestProductAPI**: Product creation with supplier relationships
- **TestInventoryTransactionAPI**: Complete inventory workflow, reservations
- **TestAPIFeatures**: Filtering, pagination, system endpoints

### `test_advanced_transactions.py`  
Advanced transaction scenarios and edge cases:
- **Stock transfers** between locations with dual transaction creation
- **Comprehensive error handling** for invalid operations
- **Inventory reservations** and release mechanisms
- **Low stock alerts** with reorder point logic

### `test_advanced_features.py`
Business intelligence and advanced API features:
- **TestAdvancedInventoryOperations**: Direct updates, location details, summary statistics
- **TestAdvancedSupplierFeatures**: Statistics, performance management, review workflows
- **TestAdvancedLocationFeatures**: Statistics, activity tracking, empty location detection  
- **TestTransactionHistoryAndFiltering**: Complex filtering, history, date ranges
- **TestEdgeCasesAndBusinessRules**: Concurrency, data consistency, complex scenarios

## Coverage Summary

- **29 comprehensive tests** covering all major functionality
- **100% API endpoint coverage** for inventory management
- **Business logic validation** including error scenarios
- **Edge case testing** for production reliability
- **Performance and concurrency** validation

## Running Tests

```bash
# Run all inventory management tests
uv run pytest tests/inventory-management/ -v

# Run specific test file
uv run pytest tests/inventory-management/test_inventory_api.py -v

# Run specific test class  
uv run pytest tests/inventory-management/test_advanced_features.py::TestAdvancedSupplierFeatures -v
```