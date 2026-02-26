from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'user', 'amount', 'method', 'status',
                    'payment_type', 'created_at')
    list_filter = ('method', 'status', 'payment_type')
    search_fields = ('booking__booking_number', 'user__username', 'mpesa_receipt', 'transaction_ref')
    readonly_fields = ('created_at', 'updated_at')
