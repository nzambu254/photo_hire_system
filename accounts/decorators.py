from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Restrict view to admin users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    return wrapper


def staff_required(view_func):
    """Restrict view to staff and admin users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ('staff', 'admin'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Staff privileges required.')
        return redirect('dashboard')
    return wrapper


def customer_required(view_func):
    """Restrict view to customer users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'customer':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return wrapper
