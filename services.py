"""
===============================================================================
Project : ERP-AR-Pro
File    : services.py
Purpose : Business Logic
===============================================================================
"""

from decimal import Decimal
from datetime import date

from sqlalchemy.orm import Session

from models import (
    Customer,
    Invoice,
    InvoiceLine,
    Payment,
    PaymentAllocation,
    JournalEntry,
    AuditLog,
)


# =============================================================================
# Audit
# =============================================================================

def log_audit(
        db: Session,
        table_name: str,
        record_id: int,
        action: str,
        user: str = "system"
):
    """
    Inserts an audit record.
    """

    audit = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        username=user
    )

    db.add(audit)


# =============================================================================
# Invoice Lookup
# =============================================================================

def get_invoice(db: Session, invoice_id: int):
    """
    Returns Invoice object.
    """

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if invoice is None:
        raise ValueError("Invoice not found.")

    return invoice


# =============================================================================
# Customer Lookup
# =============================================================================

def get_customer(db: Session, customer_id: int):
    """
    Returns Customer object.
    """

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise ValueError("Customer not found.")

    return customer


# =============================================================================
# Create Invoice
# =============================================================================

def create_invoice(
        db: Session,
        request
):
    """
    Creates Invoice Header
    Creates Invoice Lines
    Calculates Total
    Sets Balance
    """

    # Validate Customer
    get_customer(db, request.customer_id)

    # Unique Invoice Number
    existing = (
        db.query(Invoice)
        .filter(
            Invoice.invoice_number == request.invoice_number
        )
        .first()
    )

    if existing:
        raise ValueError("Invoice Number already exists.")

    invoice = Invoice(

        tenant_id=request.tenant_id,

        entity_id=request.entity_id,

        customer_id=request.customer_id,

        invoice_number=request.invoice_number,

        invoice_date=request.invoice_date,

        due_date=request.due_date,

        currency=request.currency,

        exchange_rate=request.exchange_rate,

        total_amount=Decimal("0.00"),

        balance=Decimal("0.00"),

        status="Draft"

    )

    db.add(invoice)

    db.flush()

    total = Decimal("0.00")

    for item in request.line_items:

        amount = (
            Decimal(item.quantity)
            * Decimal(item.unit_price)
        )

        line = InvoiceLine(

            invoice_id=invoice.id,

            description=item.description,

            quantity=item.quantity,

            unit_price=item.unit_price,

            amount=amount

        )

        db.add(line)

        total += amount

    invoice.total_amount = total

    invoice.balance = total

    log_audit(
        db,
        "Invoice",
        invoice.id,
        "CREATE"
    )

    db.commit()

    db.refresh(invoice)

    return invoice


# =============================================================================
# Create Journal
# =============================================================================

def create_invoice_journal(
        db: Session,
        invoice: Invoice
):
    """
    Accounting Entry

    Debit  Accounts Receivable

    Credit Revenue
    """

    journal = JournalEntry(

        invoice_id=invoice.id,

        posting_date=date.today(),

        debit_account="1100-Accounts Receivable",

        credit_account="4000-Revenue",

        amount=invoice.total_amount,

        description=f"Invoice {invoice.invoice_number}"

    )

    db.add(journal)


# =============================================================================
# Approve Invoice
# =============================================================================

def approve_invoice(
        db: Session,
        invoice_id: int
):
    """
    Draft

        ↓

    Approved

        ↓

    Generate Journal Entry
    """

    invoice = get_invoice(db, invoice_id)

    if invoice.status != "Draft":
        raise ValueError(
            "Only Draft invoices can be approved."
        )

    if len(invoice.line_items) == 0:
        raise ValueError(
            "Invoice has no line items."
        )

    if invoice.total_amount <= Decimal("0.00"):
        raise ValueError(
            "Invoice amount must be greater than zero."
        )

    invoice.status = "Approved"

    create_invoice_journal(
        db,
        invoice
    )

    log_audit(
        db,
        "Invoice",
        invoice.id,
        "APPROVE"
    )

    db.commit()

    db.refresh(invoice)

    return invoice

# =============================================================================
# Record Payment
# =============================================================================

def record_payment(db: Session, request):
    """
    Record customer payment.

    If allocations are provided:
        Allocate manually.

    Otherwise:
        Allocate automatically to oldest unpaid invoices.
    """

    # Validate Customer
    get_customer(db, request.customer_id)

    payment = Payment(
        tenant_id=request.tenant_id,
        entity_id=request.entity_id,
        customer_id=request.customer_id,
        payment_date=request.payment_date,
        amount=request.amount,
        currency=request.currency,
        reference=request.reference
    )

    db.add(payment)
    db.flush()

    remaining_amount = Decimal(request.amount)

    # ------------------------------------------------------------
    # Manual Allocation
    # ------------------------------------------------------------
    if request.allocations:
        total_allocated = Decimal("0.00")
        for item in request.allocations:
            total_allocated += Decimal(item.allocated_amount)


        if total_allocated > Decimal(request.amount):
            raise ValueError(
                "Allocated amount exceeds payment amount."
            )

        for item in request.allocations:
            if invoice.status == "Draft":
                raise ValueError(
                    "Draft invoice cannot receive payment."
                )

            invoice = get_invoice(db, item.invoice_id)

            allocation_amount = min(
                Decimal(item.allocated_amount),
                Decimal(invoice.balance)
            )

            allocation = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                allocated_amount=allocation_amount
            )

            db.add(allocation)

            invoice.balance -= allocation_amount

            if invoice.balance == Decimal("0.00"):
                invoice.status = "Paid"
            else:
                invoice.status = "Partially Paid"

    # ------------------------------------------------------------
    # Automatic Allocation
    # ------------------------------------------------------------
    else:

        invoices = (
            db.query(Invoice)
            .filter(
                Invoice.customer_id == payment.customer_id,
                Invoice.balance > 0
            )
            .order_by(Invoice.invoice_date)
            .all()
        )

        for invoice in invoices:

            if remaining_amount <= Decimal("0.00"):
                break

            allocation_amount = min(
                remaining_amount,
                Decimal(invoice.balance)
            )

            allocation = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                allocated_amount=allocation_amount
            )

            db.add(allocation)

            invoice.balance -= allocation_amount

            remaining_amount -= allocation_amount

            if invoice.balance == Decimal("0.00"):
                invoice.status = "Paid"
            else:
                invoice.status = "Partially Paid"

    # ------------------------------------------------------------
    # Create Journal Entry
    # ------------------------------------------------------------

    journal = JournalEntry(

        invoice_id=None,

        posting_date=request.payment_date,

        debit_account="1000-Cash",

        credit_account="1100-Accounts Receivable",

        amount=request.amount,

        description=f"Payment {request.reference}"

    )

    db.add(journal)

    log_audit(
        db,
        "Payment",
        payment.id,
        "CREATE"
    )

    db.commit()

    db.refresh(payment)

    return payment


# =============================================================================
# Invoice Details
# =============================================================================

def get_invoice_details(
        db: Session,
        invoice_id: int
):
    """
    Returns:

    Invoice
    Invoice Lines
    Payment Allocations
    """

    invoice = get_invoice(db, invoice_id)

    allocations = (
        db.query(PaymentAllocation)
        .filter(
            PaymentAllocation.invoice_id == invoice.id
        )
        .all()
    )

    return {
        "invoice": invoice,
        "payments": allocations
    }


# =============================================================================
# Aging Report
# =============================================================================

def get_customer_aging(
        db: Session,
        customer_id: int
):
    """
    Returns Aging Report.

    Buckets:

    Current

    1-30

    31-60

    61-90

    90+
    """

    customer = get_customer(db, customer_id)

    today = date.today()

    current = Decimal("0.00")
    days30 = Decimal("0.00")
    days60 = Decimal("0.00")
    days90 = Decimal("0.00")

    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.customer_id == customer.id,
            Invoice.balance > 0
        )
        .all()
    )

    for invoice in invoices:

        age = (today - invoice.due_date).days

        balance = Decimal(invoice.balance)

        if age <= 0:
            current += balance

        elif age <= 30:
            days30 += balance

        elif age <= 60:
            days60 += balance

        else:
            days90 += balance

    return {

        "customer_id": customer.id,

        "customer_name": customer.name,

        "current": current,

        "days30": days30,

        "days60": days60,

        "days90": days90,

        "total": (
            current +
            days30 +
            days60 +
            days90
        )

    }


# =============================================================================
# Journal Entries
# =============================================================================

def get_journal_entries(
        db: Session,
        invoice_id: int
):
    """
    Returns Journal Entries
    for an invoice.
    """

    return (
        db.query(JournalEntry)
        .filter(
            JournalEntry.invoice_id == invoice_id
        )
        .all()
    )