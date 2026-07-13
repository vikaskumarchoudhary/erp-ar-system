"""
===============================================================================
Project : ERP-AR-Pro
File    : app.py
Purpose : FastAPI Entry Point
===============================================================================
"""
from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import services
import schemas
from database import Base, engine, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ERP Accounts Receivable Prototype",
    version="1.0",
    description="Minimal Multi-Tenant ERP AR Module"
)


# =============================================================================
# Home
# =============================================================================

@app.get("/")
def home():
    return {

        "application": "ERP Accounts Receivable",

        "version": "1.0",

        "database": "SQLite",

        "framework": "FastAPI"

    }


# =============================================================================
# Health
# =============================================================================

@app.get("/health")
def health():
    return {
        "status": "UP"
    }


# =============================================================================
# Create Invoice
# =============================================================================

@app.post("/invoices")
def create_invoice(
        request: schemas.InvoiceCreate,
        tenant_id: int = Header(..., alias="X-Tenant-ID"),
        db: Session = Depends(get_db)
):
    if tenant_id != request.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant mismatch."
        )

    return services.create_invoice(db, request)


# =============================================================================
# Get Invoice
# =============================================================================

@app.get("/invoices/{invoice_id}")
def get_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    try:
        return services.get_invoice_details(
            db,
            invoice_id
        )

    except Exception as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )


# =============================================================================
# Approve Invoice
# =============================================================================

@app.post("/invoices/{invoice_id}/approve")
def approve_invoice(
        invoice_id: int,
        db: Session = Depends(get_db)
):
    try:
        return services.approve_invoice(
            db,
            invoice_id
        )

    except Exception as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )


# =============================================================================
# Record Payment
# =============================================================================

@app.post("/payments")
def record_payment(
        request: schemas.PaymentCreate,
        db: Session = Depends(get_db)
):
    total_allocated = Decimal("0.00")

    for item in request.allocations:
        total_allocated += Decimal(item.allocated_amount)

    if total_allocated > Decimal(request.amount):
        raise ValueError(
            "Allocated amount exceeds payment amount."
        )
    try:
        return services.record_payment(
            db,
            request
        )

    except Exception as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )


# =============================================================================
# Customer Aging Report
# =============================================================================

@app.get("/customers/{customer_id}/aging")
def customer_aging(
        customer_id: int,
        db: Session = Depends(get_db)
):
    try:
        return services.get_customer_aging(
            db,
            customer_id
        )

    except Exception as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )


# =============================================================================
# Journal Entries
# =============================================================================

@app.get("/journal-entries")
def journal_entries(
        invoice: int,
        db: Session = Depends(get_db)
):
    try:
        return services.get_journal_entries(
            db,
            invoice
        )

    except Exception as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )



