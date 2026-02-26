from django.db import models
from django.conf import settings
from bookings.models import Booking


class Payment(models.Model):
    """Payment records for bookings."""

    class Method(models.TextChoices):
        MPESA = 'mpesa', 'M-Pesa'
        CARD = 'card', 'Card Payment'
        CASH = 'cash', 'Cash'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    class PaymentType(models.TextChoices):
        HIRE = 'hire', 'Hire Payment'
        LATE_FEE = 'late_fee', 'Late Fee'
        DAMAGE = 'damage', 'Damage Charge'
        DEPOSIT = 'deposit', 'Security Deposit'

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=Method.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices, default=PaymentType.HIRE)

    # M-Pesa specific fields
    mpesa_phone = models.CharField(max_length=15, blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    mpesa_checkout_id = models.CharField(max_length=100, blank=True)

    # Card specific fields
    card_last_four = models.CharField(max_length=4, blank=True)
    transaction_ref = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - KES {self.amount} ({self.get_method_display()})"

    def mark_completed(self, receipt='', ref=''):
        """Mark payment as completed."""
        self.status = self.Status.COMPLETED
        if receipt:
            self.mpesa_receipt = receipt
        if ref:
            self.transaction_ref = ref
        self.save()
        # Confirm the booking
        if self.payment_type == 'hire':
            self.booking.confirm_booking()
