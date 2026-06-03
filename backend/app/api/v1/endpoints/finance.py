"""
Finance API endpoints.
Handles invoices, payments, and tuition management.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_finance
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.semester import Semester
from app.models.invoice import Invoice
from app.models.tuition_rate import TuitionRate
from app.services.finance_service import FinanceService
from app.schemas.finance import (
    TuitionRateCreate,
    TuitionRateResponse,
    InvoiceResponse,
    InvoiceGenerateRequest,
    PaymentCreate,
    PaymentResponse,
    TuitionPreview,
    FinancialSummary,
)

router = APIRouter(prefix="/finance", tags=["Finance"])


# ============ TUITION RATE ENDPOINTS ============

@router.post("/tuition-rates", response_model=TuitionRateResponse, status_code=status.HTTP_201_CREATED)
async def create_tuition_rate(
    rate_data: TuitionRateCreate,
    current_user: User = Depends(require_finance),
    db: AsyncSession = Depends(get_db),
):
    """Create tuition rate for an academic year. Requires finance or admin role."""
    # Check duplicate
    existing = await db.execute(
        select(TuitionRate).where(TuitionRate.academic_year == rate_data.academic_year)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Rate already exists for this year")

    rate = TuitionRate(**rate_data.model_dump())
    db.add(rate)
    await db.flush()
    return TuitionRateResponse.model_validate(rate)


@router.get("/tuition-rates", response_model=List[TuitionRateResponse])
async def list_tuition_rates(
    current_user: User = Depends(require_finance),
    db: AsyncSession = Depends(get_db),
):
    """List all tuition rates."""
    result = await db.execute(
        select(TuitionRate).order_by(TuitionRate.academic_year.desc())
    )
    return [TuitionRateResponse.model_validate(r) for r in result.scalars().all()]


# ============ INVOICE ENDPOINTS ============

@router.post("/invoices/generate", response_model=InvoiceResponse)
async def generate_invoice(
    request: InvoiceGenerateRequest,
    current_user: User = Depends(require_finance),
    db: AsyncSession = Depends(get_db),
):
    """Generate tuition invoice for a student. Calculates with scholarship."""
    service = FinanceService(db)
    invoice = await service.generate_invoice(request.student_id, request.semester_id)

    return InvoiceResponse(
        id=invoice.id,
        student_id=invoice.student_id,
        semester_id=invoice.semester_id,
        credit_hours_cost=float(invoice.credit_hours_cost),
        fixed_fees=float(invoice.fixed_fees),
        scholarship_discount=float(invoice.scholarship_discount),
        total_amount=float(invoice.total_amount),
        paid_amount=float(invoice.paid_amount),
        remaining_amount=float(invoice.total_amount) - float(invoice.paid_amount),
        status=invoice.status,
        due_date=invoice.due_date,
        created_at=invoice.created_at,
    )


@router.get("/invoices/my", response_model=List[InvoiceResponse])
async def get_my_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get invoices for the current student."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    service = FinanceService(db)
    invoices = await service.get_student_invoices(student.id)

    return [
        InvoiceResponse(
            id=inv.id,
            student_id=inv.student_id,
            semester_id=inv.semester_id,
            credit_hours_cost=float(inv.credit_hours_cost),
            fixed_fees=float(inv.fixed_fees),
            scholarship_discount=float(inv.scholarship_discount),
            total_amount=float(inv.total_amount),
            paid_amount=float(inv.paid_amount),
            remaining_amount=float(inv.total_amount) - float(inv.paid_amount),
            status=inv.status,
            due_date=inv.due_date,
            created_at=inv.created_at,
        )
        for inv in invoices
    ]


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get invoice details."""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return InvoiceResponse(
        id=invoice.id,
        student_id=invoice.student_id,
        semester_id=invoice.semester_id,
        credit_hours_cost=float(invoice.credit_hours_cost),
        fixed_fees=float(invoice.fixed_fees),
        scholarship_discount=float(invoice.scholarship_discount),
        total_amount=float(invoice.total_amount),
        paid_amount=float(invoice.paid_amount),
        remaining_amount=float(invoice.total_amount) - float(invoice.paid_amount),
        status=invoice.status,
        due_date=invoice.due_date,
        created_at=invoice.created_at,
    )


# ============ PAYMENT ENDPOINTS ============

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def record_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(require_finance),
    db: AsyncSession = Depends(get_db),
):
    """Record a payment against an invoice."""
    service = FinanceService(db)
    payment = await service.record_payment(payment_data)
    return PaymentResponse.model_validate(payment)


@router.get("/preview/{student_id}/{semester_id}", response_model=TuitionPreview)
async def preview_tuition(
    student_id: UUID,
    semester_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Preview tuition calculation for a student."""
    service = FinanceService(db)
    return await service.preview_tuition(student_id, semester_id)


# ============ REPORTS ============

@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: User = Depends(require_finance),
    db: AsyncSession = Depends(get_db),
):
    """Get financial summary report. Requires finance or admin role."""
    service = FinanceService(db)
    return await service.get_financial_summary()
