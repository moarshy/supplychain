"""
Test configuration and fixtures.
"""
import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from decimal import Decimal

from src.data.database import get_session
from src.api.main import app
from src.data.models import Supplier, Location, Product, SupplierCreate, LocationCreate, ProductCreate


# Test database engine (in-memory SQLite)
@pytest.fixture(scope="function")
def engine():
    """Create fresh test database engine for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function") 
def session(engine):
    """Create fresh test database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(session: Session):
    """Create test client with fresh database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_supplier")
def sample_supplier_fixture(session: Session):
    """Create a sample supplier for testing."""
    supplier = Supplier(
        name="Test Supplier",
        contact_person="John Doe",
        email="john@testsupplier.com",
        phone="+1-555-0123",
        lead_time_days=5,
        payment_terms="Net 30",
        minimum_order_qty=10
    )
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@pytest.fixture(name="sample_location")
def sample_location_fixture(session: Session):
    """Create a sample location for testing."""
    location = Location(
        name="Test Warehouse",
        code="TEST",
        address="123 Test St, Test City, TC 12345",
        warehouse_type="Distribution"
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@pytest.fixture(name="sample_product")
def sample_product_fixture(session: Session, sample_supplier: Supplier):
    """Create a sample product for testing."""
    product = Product(
        sku="TEST-001",
        name="Test Product",
        description="A test product",
        category="Test Category",
        unit_cost=Decimal("10.00"),
        unit_price=Decimal("20.00"),
        reorder_point=5,
        reorder_quantity=25,
        supplier_id=sample_supplier.id
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture(name="sample_data")
def sample_data_fixture(session: Session):
    """Create complete sample data set for testing."""
    # Create supplier
    supplier = Supplier(
        name="Complete Test Supplier",
        contact_person="Jane Smith",
        email="jane@completesupplier.com",
        lead_time_days=7,
        payment_terms="Net 15",
        minimum_order_qty=20
    )
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    
    # Create location
    location = Location(
        name="Complete Test Location",
        code="COMP",
        address="456 Complete Ave, Complete City",
        warehouse_type="Warehouse"
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    
    # Create product
    product = Product(
        sku="COMP-001",
        name="Complete Test Product",
        description="A complete test product",
        category="Complete Category",
        unit_cost=Decimal("15.00"),
        unit_price=Decimal("30.00"),
        reorder_point=10,
        reorder_quantity=50,
        supplier_id=supplier.id
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return {
        "supplier": supplier,
        "location": location,
        "product": product
    }