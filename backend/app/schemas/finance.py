"""
Finance schemas - request/response models for invoices and payments.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from app.models.invoice import InvoiceStatus
from app.models.payment import PaymentMethod, PaymentStatus


class TuitionRateCreate(BaseModel):
    """Create a tuition rate for an academic year."""
    academic_year: str = Field(..., pattern=r"^\d{4}/\d{4}$")
    cost_per_hour: float = Field(..., gt=0)
    fixed_fees: float = Field(..., ge=0)


class TuitionRateResponse(BaseModel):
    """Tuition rate response."""
    id: UUID
    academic_year: str
    cost_per_hour: float
    fixed_fees: float
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Invoice details response."""
    id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    semester_id: UUID
    semester_name: Optional[str] = None
    credit_hours_cost: float
    fixed_fees: float
    scholarship_discount: float
    total_amount: float
    paid_amount: float
    remaining_amount: float
    status: InvoiceStatus
    due_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceGenerateRequest(BaseModel):
    """Request to generate invoice for a student."""
    student_id: UUID
    semester_id: UUID


class PaymentCreate(BaseModel):
    """Record a payment."""
    invoice_id: UUID
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_ref: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment record response."""
    id: UUID
    invoice_id: UUID
    amount: float
    payment_method: PaymentMethod
    transaction_ref: Optional[str] = None
    status: PaymentStatus
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TuitionPreview(BaseModel):
    """Preview tuition calculation before enrollment."""
    credit_hours: int
    cost_per_hour: float
    credit_hours_cost: float
    fixed_fees: float
    scholarship_discount: float
    scholarship_percentage: float
    total_amount: float


class FinancialSummary(BaseModel):
    """Financial summary for reports."""
    total_invoiced: float
    total_collected: float
    total_outstanding: float
    total_scholarships: float
    payment_method_breakdown: dict
    invoice_status_breakdown: dict
