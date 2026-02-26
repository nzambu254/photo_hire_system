from django import template

register = template.Library()


@register.filter
def has_role(user, role):
    """Check if user has a specific role. Usage: {% if user|has_role:'admin' %}"""
    if not user.is_authenticated:
        return False
    return user.role == role


@register.filter
def is_staff_or_admin(user):
    """Check if user is staff or admin."""
    if not user.is_authenticated:
        return False
    return user.role in ('staff', 'admin')
