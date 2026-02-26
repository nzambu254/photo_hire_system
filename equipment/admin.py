from django.contrib import admin
from .models import Category, Equipment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_count', 'available_count')
    search_fields = ('name',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'serial_number', 'daily_rate', 'status', 'is_active')
    list_filter = ('category', 'status', 'is_active')
    search_fields = ('name', 'serial_number', 'brand')
