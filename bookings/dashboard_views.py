from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from bookings.models import Booking
from equipment.models import Equipment, Category
from payments.models import Payment
from accounts.models import User


@login_required
def dashboard(request):
    """Route to appropriate dashboard based on user role."""
    if request.user.role == 'admin':
        return admin_dashboard(request)
    elif request.user.role == 'staff':
        return staff_dashboard(request)
    else:
        return customer_dashboard(request)


def customer_dashboard(request):
    """Dashboard for customers."""
    bookings = Booking.objects.filter(customer=request.user)
    context = {
        'active_bookings': bookings.filter(status__in=['confirmed', 'issued']),
        'pending_bookings': bookings.filter(status='pending'),
        'total_bookings': bookings.count(),
        'total_spent': bookings.filter(status='returned').aggregate(
            total=Sum('total_amount'))['total'] or 0,
    }
    return render(request, 'dashboard/customer.html', context)


def staff_dashboard(request):
    """Dashboard for staff."""
    today = timezone.now().date()
    context = {
        'pending_bookings': Booking.objects.filter(status='confirmed').count(),
        'active_hires': Booking.objects.filter(status='issued').count(),
        'overdue_count': Booking.objects.filter(status='issued', end_date__lt=today).count(),
        'today_returns': Booking.objects.filter(end_date=today, status='issued').count(),
        'recent_bookings': Booking.objects.filter(
            status__in=['confirmed', 'issued', 'overdue']
        ).order_by('-created_at')[:10],
        'overdue_bookings': Booking.objects.filter(
            status='issued', end_date__lt=today
        ).order_by('end_date')[:5],
    }
    return render(request, 'dashboard/staff.html', context)


def admin_dashboard(request):
    """Dashboard for admins."""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    # Revenue
    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    month_revenue = Payment.objects.filter(
        status='completed', created_at__date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_users': User.objects.count(),
        'total_customers': User.objects.filter(role='customer').count(),
        'total_staff': User.objects.filter(role='staff').count(),
        'total_equipment': Equipment.objects.filter(is_active=True).count(),
        'available_equipment': Equipment.objects.filter(status='available', is_active=True).count(),
        'hired_equipment': Equipment.objects.filter(status='hired').count(),
        'total_bookings': Booking.objects.count(),
        'active_bookings': Booking.objects.filter(status__in=['confirmed', 'issued']).count(),
        'overdue_count': Booking.objects.filter(status='issued', end_date__lt=today).count(),
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'recent_bookings': Booking.objects.order_by('-created_at')[:10],
        'recent_payments': Payment.objects.order_by('-created_at')[:10],
        'categories': Category.objects.all(),
    }
    return render(request, 'dashboard/admin.html', context)
