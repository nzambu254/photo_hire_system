from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Liz Web Info', {'fields': ('role', 'phone_number', 'id_number', 'address')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Liz Web Info', {'fields': ('role', 'phone_number', 'id_number')}),
    )
