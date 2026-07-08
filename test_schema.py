from datetime import date

from schemas import InvoiceCreate

invoice = InvoiceCreate(
    tenant_id=1,
    entity_id=1,
    customer_id=1,
    invoice_number="INV-1001",
    invoice_date=date.today(),
    due_date=date.today(),
    currency="USD",
    exchange_rate=1.0,
    line_items=[
        {
            "description": "Laptop",
            "quantity": 2,
            "unit_price": 500
        },
        {
            "description": "Mouse",
            "quantity": 1,
            "unit_price": 20
        }
    ]
)

print(invoice)