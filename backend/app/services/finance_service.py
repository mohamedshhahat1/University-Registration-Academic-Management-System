"""
Finance service - handles tuition calculation, invoicing, and payments.
Implements cohort-based pricing and scholarship engine.
"""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.student import Student
from app.models.semester import Semester
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.tuition_rate import TuitionRate
from app.models.registration_cart import RegistrationCart, CartStatus
from app.schemas.finance import (
    TuitionPreview,
    PaymentCreate,
    FinancialSummary,
)


class FinanceService:
    """Service for financial operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_scholarship_discount(self, cgpa: float, subtotal: float) -> tuple:
        """
        Calculate scholarship discount based on CGPA.
        
        Rules:
            CGPA >= 3.7 → 20% discount
            CGPA >= 3.3 → 10% discount
            Otherwise  → 0%
        
        Returns:
            (discount_amount, discount_percentage)
        """
        if cgpa >= settings.SCHOLARSHIP_HIGH_THRESHOLD:
            percentage = settings.SCHOLARSHIP_HIGH_DISCOUNT
        elif cgpa >= settings.SCHOLARSHIP_MID_THRESHOLD:
            percentage = settings.SCHOLARSHIP_MID_DISCOUNT
        else:
            percentage = 0.0

        discount = subtotal * percentage
        return round(discount, 2), percentage

    async def get_tuition_rate(self, admission_year: int) -> TuitionRate:
        """
        Get tuition rate for a student's admission year (cohort-based pricing).
        Student keeps the tuition rate of their admission year.
        """
        academic_year = f"{admission_year}/{admission_year + 1}"
        result = await self.db.execute(
            select(TuitionRate).where(TuitionRate.academic_year == academic_year)
        )
        rate = result.scalar_one_or_none()
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tuition rate found for academic year {academic_year}",
            )
        return rate

    async def preview_tuition(
        self, student_id: UUID, semester_id: UUID
    ) -> TuitionPreview:
        """
        Preview tuition calculation before enrollment.
        Shows breakdown: credit hours cost + fixed fees - scholarship = total
        """
        # Get student
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get tuition rate (cohort-based)
        rate = await self.get_tuition_rate(student.admission_year)

        # Get total credit hours from cart
        cart_result = await self.db.execute(
            select(RegistrationCart).where(
                and_(
                    RegistrationCart.student_id == student_id,
                    RegistrationCart.semester_id == semester_id,
                    RegistrationCart.status.in_([
                        CartStatus.DRAFT,
                        CartStatus.SUBMITTED,
                        CartStatus.APPROVED,
                    ]),
                )
            )
        )
        cart = cart_result.scalar_one_or_none()
        credit_hours = cart.total_hours if cart else 0

        # Calculate costs
        credit_hours_cost = round(credit_hours * float(rate.cost_per_hour), 2)
        fixed_fees = float(rate.fixed_fees)
        subtotal = credit_hours_cost + fixed_fees

        # Calculate scholarship
        discount, percentage = self._calculate_scholarship_discount(
            float(student.cgpa), subtotal
        )

        total = round(subtotal - discount, 2)

        return TuitionPreview(
            credit_hours=credit_hours,
            cost_per_hour=float(rate.cost_per_hour),
            credit_hours_cost=credit_hours_cost,
            fixed_fees=fixed_fees,
            scholarship_discount=discount,
            scholarship_percentage=percentage,
            total_amount=total,
        )

    async def generate_invoice(
        self, student_id: UUID, semester_id: UUID
    ) -> Invoice:
        """
        Generate tuition invoice for a student's semester registration.
        Uses cohort-based tuition rate and applies scholarship discount.
        """
        # Check if invoice already exists
        existing = await self.db.execute(
            select(Invoice).where(
                and_(
                    Invoice.student_id == student_id,
                    Invoice.semester_id == semester_id,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invoice already exists for this semester",
            )

        # Calculate tuition
        preview = await self.preview_tuition(student_id, semester_id)

        # Create invoice
        invoice = Invoice(
            student_id=student_id,
            semester_id=semester_id,
            credit_hours_cost=preview.credit_hours_cost,
            fixed_fees=preview.fixed_fees,
            scholarship_discount=preview.scholarship_discount,
            total_amount=preview.total_amount,
            paid_amount=0.00,
            status=InvoiceStatus.PENDING,
            due_date=date.today(),  # TODO: Configure due date from semester
        )
        self.db.add(invoice)
        await self.db.flush()

        return invoice

    async def record_payment(self, payment_data: PaymentCreate) -> Payment:
        """
        Record a payment against an invoice.
        Updates invoice paid_amount and status accordingly.
        """
        # Get invoice
        invoice_result = await self.db.execute(
            select(Invoice).where(Invoice.id == payment_data.invoice_id)
        )
        invoice = invoice_result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot pay invoice with status: {invoice.status.value}",
            )

        remaining = float(invoice.total_amount) - float(invoice.paid_amount)
        if payment_data.amount > remaining:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount ({payment_data.amount}) exceeds remaining balance ({remaining})",
            )

        # Create payment record
        payment = Payment(
            invoice_id=payment_data.invoice_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            transaction_ref=payment_data.transaction_ref,
            status=PaymentStatus.COMPLETED,
            paid_at=datetime.utcnow(),
        )
        self.db.add(payment)

        # Update invoice
        invoice.paid_amount = float(invoice.paid_amount) + payment_data.amount
        if float(invoice.paid_amount) >= float(invoice.total_amount):
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIAL

        await self.db.flush()
        return payment

    async def get_student_invoices(self, student_id: UUID) -> list:
        """Get all invoices for a student."""
        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.student_id == student_id)
            .order_by(Invoice.created_at.desc())
        )
        return result.scalars().all()

    async def get_financial_summary(self) -> FinancialSummary:
        """Generate financial summary report."""
        # Total invoiced
        total_invoiced = await self.db.execute(
            select(func.sum(Invoice.total_amount)).where(
                Invoice.status != InvoiceStatus.CANCELLED
            )
        )
        # Total collected
        total_collected = await self.db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == PaymentStatus.COMPLETED
            )
        )
        # Total outstanding
        total_outstanding = await self.db.execute(
            select(func.sum(Invoice.total_amount - Invoice.paid_amount)).where(
                Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.PARTIAL])
            )
        )
        # Total scholarships
        total_scholarships = await self.db.execute(
            select(func.sum(Invoice.scholarship_discount)).where(
                Invoice.status != InvoiceStatus.CANCELLED
            )
        )

        return FinancialSummary(
            total_invoiced=float(total_invoiced.scalar() or 0),
            total_collected=float(total_collected.scalar() or 0),
            total_outstanding=float(total_outstanding.scalar() or 0),
            total_scholarships=float(total_scholarships.scalar() or 0),
            payment_method_breakdown={},
            invoice_status_breakdown={},
        )
