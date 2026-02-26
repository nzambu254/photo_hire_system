from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Equipment categories: Cameras, Lenses, Lighting Kits, Tripods, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-camera', help_text='Bootstrap icon class')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def available_count(self):
        return self.equipment_set.filter(status='available').count()

    @property
    def total_count(self):
        return self.equipment_set.count()


class Equipment(models.Model):
    """Individual equipment items available for hire."""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        HIRED = 'hired', 'Hired Out'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
        RESERVED = 'reserved', 'Reserved'

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, unique=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text='Daily hire rate in KES')
    replacement_value = models.DecimalField(max_digits=12, decimal_places=2, help_text='Value for damage assessment')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AVAILABLE)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, help_text='External image URL (used if no uploaded image)')
    condition_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Equipment'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE and self.is_active

    @property
    def display_rate(self):
        return f"KES {self.daily_rate:,.2f}"

    @property
    def get_image_url(self):
        """Return uploaded image URL, external URL, or None."""
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None
