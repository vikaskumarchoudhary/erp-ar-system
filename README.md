# erp-ar-system

# ERP-AR-Pro Prototype

## Overview

ERP-AR-Pro is a lightweight prototype of an **Accounts Receivable (AR) and Invoicing Module** for a multi-tenant ERP system.

The prototype demonstrates core financial system concepts including:

- Multi-Tenant Architecture
- Multi-Entity Support
- Customer Invoice Management
- Invoice Approval Workflow
- General Ledger (GL) Posting
- Accounts Receivable
- Payment Allocation
- Partial Payments
- Customer Aging Report
- Audit Logging

This project is intentionally simplified for demonstration purposes while following enterprise financial system principles.

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | SQLite |
| API Documentation | Swagger UI |
| Validation | Pydantic |

---

# Project Structure

```
erp-ar-prototype/

│
├── app.py
├── database.py
├── models.py
├── schemas.py
├── services.py
├── seed.py
├── requirements.txt
└── README.md
```

---

# Features

Implemented

- Create Invoice
- Invoice Line Items
- Invoice Approval
- Automatic Journal Entry Creation
- Record Payment
- Manual Payment Allocation
- Automatic Payment Allocation
- Partial Payments
- Customer Aging Report
- Journal Entry Lookup
- Basic Audit Logging

Prototype Features

- Multi-Tenant Support
- Multi-Entity Support
- Multi-Currency Fields
- Exchange Rate Storage

---

# Financial Workflow

```
Customer

      │

      ▼

Create Invoice

      │

      ▼

Status = Draft

      │

Approve Invoice

      │

      ▼

Generate Journal Entry

      │

      ▼

Debit Accounts Receivable

Credit Revenue

      │

Receive Payment

      │

      ▼

Allocate Payment

      │

      ▼

Update Balance

      │

      ▼

Paid / Partially Paid

```

---

# Installation

## 1 Clone Repository

```bash
git clone <repository-url>

cd erp-ar-prototype
```

---

## 2 Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4 Seed Database

```bash
python seed.py
```

Expected Output

```
Database Seeded Successfully

Tenant ID : 1

Entity ID : 1

Customer ID : 1
```

---

## 5 Run Application

```bash
uvicorn app:app --reload
```

Expected

```
INFO: Application started

Running on

http://127.0.0.1:8000
```

---

## 6 Open Swagger

```
http://127.0.0.1:8000/docs
```

---

# API Endpoints

| Method | Endpoint | Description |
|----------|-----------------------------|-----------------------------|
| POST | /invoices | Create Invoice |
| GET | /invoices/{id} | Get Invoice |
| POST | /invoices/{id}/approve | Approve Invoice |
| POST | /payments | Record Payment |
| GET | /customers/{id}/aging | Customer Aging |
| GET | /journal-entries/{invoice_id} | Journal Entries |

---

# Testing Sequence

The following sequence demonstrates the complete workflow.

---

## Step 1 Create Invoice

POST

```
/invoices
```

Headers

```
X-Tenant-ID : 1
```

Request

```json
{
  "tenant_id": 1,
  "entity_id": 1,
  "customer_id": 1,
  "invoice_number": "INV-1001",
  "invoice_date": "2026-07-08",
  "due_date": "2026-08-08",
  "currency": "INR",
  "exchange_rate": 1,
  "line_items": [
    {
      "description": "Laptop",
      "quantity": 2,
      "unit_price": 50000
    },
    {
      "description": "Mouse",
      "quantity": 5,
      "unit_price": 500
    }
  ]
}
```

Expected

```
Invoice Created

Status = Draft

Total = 102500

Balance = 102500
```

---

## Step 2 Get Invoice

GET

```
/invoices/1
```

Expected

```
Invoice Header

Invoice Lines

Balance

Status
```

---

## Step 3 Approve Invoice

POST

```
/invoices/1/approve
```

Expected

```
Invoice Status

Approved
```

Automatically creates GL Entry

```
Debit

Accounts Receivable

Credit

Revenue
```

---

## Step 4 View Journal

GET

```
/journal-entries/1
```

Expected

```
Debit Account

1100-Accounts Receivable

Credit Account

4000-Revenue

Amount

102500
```

---

## Step 5 Record Payment

POST

```
/payments
```

Request

```json
{
  "tenant_id": 1,
  "entity_id": 1,
  "customer_id": 1,
  "payment_date": "2026-07-09",
  "amount": 50000,
  "currency": "INR",
  "reference": "PAY001"
}
```

Expected

```
Invoice Status

Partially Paid

Balance

52500
```

---

## Step 6 Invoice Details

GET

```
/invoices/1
```

Expected

```
Payment History

Remaining Balance

Status

Partially Paid
```

---

## Step 7 Aging Report

GET

```
/customers/1/aging
```

Expected

```json
{
    "customer_id":1,
    "customer_name":"ABC Technologies",
    "current":52500,
    "days30":0,
    "days60":0,
    "days90":0,
    "total":52500
}
```

---

# Database Tables

```
Tenant

Entity

Customer

Invoice

InvoiceLine

Payment

PaymentAllocation

JournalEntry

AuditLog
```

---

# Invoice Lifecycle

```
Draft

↓

Approved

↓

Partially Paid

↓

Paid
```

---

# Journal Entries

Invoice Approval

```
Debit

Accounts Receivable

Credit

Revenue
```

Payment

```
Debit

Cash

Credit

Accounts Receivable
```

---

# Assumptions

- SQLite is used for simplicity.
- One base currency per Entity.
- Exchange rate stored at invoice level.
- Revenue recognized immediately on approval.
- No authentication.
- Tenant supplied through request header.
- Prototype intended for demonstration only.

---

# Future Enhancements

- JWT Authentication
- Role Based Access Control
- Credit Memo Processing
- Revenue Recognition Schedule
- Exchange Rate Master
- Intercompany Transactions
- Period Close
- GL Reconciliation
- SOX Audit Reports
- Docker Deployment

---

# Author

**Vikas Kumar Choudhary**

ERP Accounts Receivable Prototype

Python • FastAPI • SQLAlchemy • Financial Systems