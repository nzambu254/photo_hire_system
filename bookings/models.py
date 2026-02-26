from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from equipment.models import Equipment


class Booking(models.Model):
    """Customer booking for equipment hire."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Payment'
        CONFIRMED = 'confirmed', 'Confirmed'
        ISSUED = 'issued', 'Equipment Issued'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'

    booking_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    # Staff tracking
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='issued_bookings'
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    returned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='received_returns'
    )

    # Late / Damage charges
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_number} - {self.equipment.name}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self._generate_booking_number()
        if not self.total_amount:
            self.total_amount = self.calculate_hire_cost()
        super().save(*args, **kwargs)

    def _generate_booking_number(self):
        """Generate unique booking number like LIZ-20250001."""
        from datetime import date
        year = date.today().year
        last = Booking.objects.filter(
            booking_number__startswith=f'LIZ-{year}'
        ).order_by('-booking_number').first()
        if last:
            last_num = int(last.booking_number.split('-')[1][4:])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'LIZ-{year}{new_num:04d}'

    @property
    def hire_days(self):
        """Number of hire days."""
        return (self.end_date - self.start_date).days + 1

    def calculate_hire_cost(self):
        """Calculate base hire cost."""
        return self.equipment.daily_rate * self.hire_days

    @property
    def overdue_days(self):
        """Number of days overdue."""
        if self.status in ('issued', 'overdue'):
            today = timezone.now().date()
            if today > self.end_date:
                return (today - self.end_date).days
        return 0

    def calculate_late_fee(self):
        """Calculate late return fee."""
        if self.overdue_days > 0:
            daily_late = self.equipment.daily_rate * Decimal(str(settings.LATE_FEE_PER_DAY_PERCENT / 100))
            return daily_late * self.overdue_days
        return Decimal('0.00')

    @property
    def grand_total(self):
        """Total including late fees and damage charges."""
        return self.total_amount + self.late_fee + self.damage_fee

    @property
    def is_overdue(self):
        return self.overdue_days > 0

    def confirm_booking(self):
        """Mark booking as confirmed after payment."""
        self.status = self.Status.CONFIRMED
        self.equipment.status = Equipment.Status.RESERVED
        self.equipment.save()
        self.save()

    def issue_equipment(self, staff_user):
        """Staff issues equipment to customer."""
        self.status = self.Status.ISSUED
        self.issued_by = staff_user
        self.issued_at = timezone.now()
        self.equipment.status = Equipment.Status.HIRED
        self.equipment.save()
        self.save()

    def return_equipment(self, staff_user, damage_fee=0, damage_notes=''):
        """Process equipment return."""
        self.status = self.Status.RETURNED
        self.returned_at = timezone.now()
        self.returned_to = staff_user
        self.late_fee = self.calculate_late_fee()
        self.damage_fee = Decimal(str(damage_fee))
        self.damage_notes = damage_notes
        self.equipment.status = Equipment.Status.AVAILABLE
        self.equipment.save()
        self.save()

    def cancel_booking(self):
        """Cancel the booking."""
        self.status = self.Status.CANCELLED
        if self.equipment.status in ('reserved',):
            self.equipment.status = Equipment.Status.AVAILABLE
            self.equipment.save()
        self.save()
