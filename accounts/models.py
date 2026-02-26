from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access for Liz Web."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
        CUSTOMER = 'customer', 'Customer'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    id_number = models.CharField(max_length=20, blank=True, verbose_name='ID Number')
    address = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def is_staff_user(self):
        return self.role == self.Role.STAFF

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER
