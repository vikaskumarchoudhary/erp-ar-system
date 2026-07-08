"""
===============================================================================
Project : ERP-AR-Pro
File    : schemas.py
Purpose : Pydantic Schemas
===============================================================================
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# OopCompanion:suppressRename


# =============================================================================
# Invoice Line
# =============================================================================

class InvoiceLineCreate(BaseModel):
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


class InvoiceLineResponse(BaseModel):
    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Create Invoice Request
# =============================================================================

class InvoiceCreate(BaseModel):
    tenant_id: int
    entity_id: int
    customer_id: int

    invoice_number: str

    invoice_date: date

    due_date: date

    currency: str = "USD"

    exchange_rate: Decimal = Decimal("1.0000")

    line_items: List[InvoiceLineCreate]


# =============================================================================
# Invoice Response
# =============================================================================

class InvoiceResponse(BaseModel):

    id: int

    invoice_number: str

    invoice_date: date

    due_date: date

    currency: str

    total_amount: Decimal

    balance: Decimal

    status: str

    line_items: List[InvoiceLineResponse]

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Payment Allocation
# =============================================================================

class PaymentAllocationRequest(BaseModel):

    invoice_id: int

    allocated_amount: Decimal = Field(gt=0)


# =============================================================================
# Record Payment Request
# =============================================================================

class PaymentCreate(BaseModel):

    tenant_id: int

    entity_id: int

    customer_id: int

    payment_date: date

    amount: Decimal = Field(gt=0)

    currency: str

    reference: str

    # Optional
    # If omitted, payment will automatically
    # allocate to oldest invoices.
    allocations: Optional[
        List[PaymentAllocationRequest]
    ] = None


# =============================================================================
# Payment Response
# =============================================================================

class PaymentResponse(BaseModel):

    id: int

    payment_date: date

    amount: Decimal

    currency: str

    reference: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Journal Entry Response
# =============================================================================

class JournalResponse(BaseModel):

    id: int

    posting_date: date

    debit_account: str

    credit_account: str

    amount: Decimal

    description: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Aging Report
# =============================================================================

class AgingResponse(BaseModel):

    customer_id: int

    customer_name: str

    current: Decimal

    days30: Decimal

    days60: Decimal

    days90: Decimal

    total: Decimal


# =============================================================================
# Generic Message
# =============================================================================

class MessageResponse(BaseModel):

    message: str