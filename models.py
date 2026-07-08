"""
===============================================================================
Project : ERP-AR-Pro
File    : models.py
Purpose : Database Models
===============================================================================
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    Numeric
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database import Base


# OopCompanion:suppressRename


# ============================================================================
# Tenant
# ============================================================================

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    entities: Mapped[List["Entity"]] = relationship(back_populates="tenant")


# ============================================================================
# Entity
# ============================================================================

class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id")
    )

    name: Mapped[str] = mapped_column(String(100))

    base_currency: Mapped[str] = mapped_column(
        String(10),
        default="USD"
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="entities")

    customers: Mapped[List["Customer"]] = relationship(
        back_populates="entity"
    )


# ============================================================================
# Customer
# ============================================================================

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int]

    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id")
    )

    customer_code: Mapped[str] = mapped_column(
        String(30),
        unique=True
    )

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(String(150))

    entity: Mapped["Entity"] = relationship(
        back_populates="customers"
    )

    invoices: Mapped[List["Invoice"]] = relationship(
        back_populates="customer"
    )

    payments: Mapped[List["Payment"]] = relationship(
        back_populates="customer"
    )


# ============================================================================
# Invoice
# ============================================================================

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int]

    entity_id: Mapped[int]

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    invoice_number: Mapped[str] = mapped_column(
        String(30),
        unique=True
    )

    invoice_date: Mapped[date]

    due_date: Mapped[date]

    currency: Mapped[str] = mapped_column(String(10))

    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        default=1
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Draft"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="invoices"
    )

    line_items: Mapped[List["InvoiceLine"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan"
    )


# ============================================================================
# Invoice Line
# ============================================================================

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(primary_key=True)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id")
    )

    description: Mapped[str] = mapped_column(String(200))

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="line_items"
    )


# ============================================================================
# Payment
# ============================================================================

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int]

    entity_id: Mapped[int]

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    payment_date: Mapped[date]

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    currency: Mapped[str] = mapped_column(
        String(10)
    )

    reference: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="payments"
    )

    allocations: Mapped[List["PaymentAllocation"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan"
    )


# ============================================================================
# Payment Allocation
# ============================================================================

class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[int] = mapped_column(primary_key=True)

    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id")
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id")
    )

    allocated_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    payment: Mapped["Payment"] = relationship(
        back_populates="allocations"
    )

    invoice: Mapped["Invoice"] = relationship()


# ============================================================================
# Journal Entry
# ============================================================================

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"),
        nullable=True
    )

    posting_date: Mapped[date]

    debit_account: Mapped[str] = mapped_column(
        String(100)
    )

    credit_account: Mapped[str] = mapped_column(
        String(100)
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    description: Mapped[str] = mapped_column(
        String(200)
    )


# ============================================================================
# Audit Log
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    table_name: Mapped[str] = mapped_column(
        String(50)
    )

    record_id: Mapped[int]

    action: Mapped[str] = mapped_column(
        String(50)
    )

    username: Mapped[str] = mapped_column(
        String(50),
        default="system"
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )