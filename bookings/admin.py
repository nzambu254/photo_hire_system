from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'customer', 'equipment', 'start_date',
                    'end_date', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'start_date')
    search_fields = ('booking_number', 'customer__username', 'equipment__name')
    readonly_fields = ('booking_number', 'created_at', 'updated_at')
