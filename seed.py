"""
===============================================================================
Project : ERP-AR-Pro
File    : seed.py
Purpose : Insert Sample Data
===============================================================================
"""

from database import Base, engine, SessionLocal
from models import Tenant, Entity, Customer

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:

    # -------------------------------------------------------
    # Clear Existing Data (Demo Only)
    # -------------------------------------------------------

    db.query(Customer).delete()
    db.query(Entity).delete()
    db.query(Tenant).delete()

    db.commit()

    # -------------------------------------------------------
    # Tenant
    # -------------------------------------------------------

    tenant = Tenant(
        name="Demo Corporation"
    )

    db.add(tenant)
    db.flush()

    # -------------------------------------------------------
    # Entity
    # -------------------------------------------------------

    entity = Entity(
        tenant_id=tenant.id,
        name="Demo India Pvt Ltd",
        base_currency="INR"
    )

    db.add(entity)
    db.flush()

    # -------------------------------------------------------
    # Customer
    # -------------------------------------------------------

    customer = Customer(
        tenant_id=tenant.id,
        entity_id=entity.id,
        customer_code="CUST001",
        name="ABC Technologies",
        email="accounts@abctech.com"
    )

    db.add(customer)

    db.commit()

    print("=" * 60)
    print("Database Seeded Successfully")
    print("=" * 60)
    print(f"Tenant ID   : {tenant.id}")
    print(f"Entity ID   : {entity.id}")
    print(f"Customer ID : {customer.id}")
    print("=" * 60)

except Exception as ex:

    db.rollback()

    print(ex)

finally:

    db.close()