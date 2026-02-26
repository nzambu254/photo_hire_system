from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count
from .models import Booking
from .forms import BookingForm, ReturnForm
from equipment.models import Equipment
from accounts.decorators import staff_required, customer_required, admin_required


@login_required
@customer_required
def create_booking(request, equipment_id):
    """Customer: create a new booking."""
    item = get_object_or_404(Equipment, pk=equipment_id, is_active=True)
    if not item.is_available:
        messages.error(request, 'This equipment is not currently available for hire.')
        return redirect('equipment_detail', pk=equipment_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.total_amount = booking.calculate_hire_cost()
            booking.save()
            messages.success(request, f'Booking {booking.booking_number} created! Please proceed to payment.')
            return redirect('booking_payment', pk=booking.pk)
    else:
        form = BookingForm(initial={'equipment': item})

    return render(request, 'bookings/create.html', {'form': form, 'item': item})


@login_required
def booking_detail(request, pk):
    """View booking details."""
    booking = get_object_or_404(Booking, pk=pk)
    # Customers can only see their own bookings
    if request.user.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def my_bookings(request):
    """Customer: view their bookings."""
    bookings = Booking.objects.filter(customer=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings, 'status_filter': status_filter})


@login_required
@staff_required
def all_bookings(request):
    """Staff/Admin: view all bookings."""
    bookings = Booking.objects.all()
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if search:
        bookings = bookings.filter(
            Q(booking_number__icontains=search) |
            Q(customer__username__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(equipment__name__icontains=search)
        )

    return render(request, 'bookings/all_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'search': search,
    })


@login_required
@staff_required
def issue_equipment(request, pk):
    """Staff: issue equipment to customer."""
    booking = get_object_or_404(Booking, pk=pk, status='confirmed')
    if request.method == 'POST':
        booking.issue_equipment(request.user)
        messages.success(request, f'Equipment issued for booking {booking.booking_number}.')
        return redirect('all_bookings')
    return render(request, 'bookings/issue_confirm.html', {'booking': booking})


@login_required
@staff_required
def return_equipment(request, pk):
    """Staff: process equipment return."""
    booking = get_object_or_404(Booking, pk=pk, status__in=['issued', 'overdue'])
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            booking.return_equipment(
                staff_user=request.user,
                damage_fee=form.cleaned_data['damage_fee'],
                damage_notes=form.cleaned_data['damage_notes'],
            )
            messages.success(request,
                f'Return processed for {booking.booking_number}. '
                f'Late fee: KES {booking.late_fee:,.2f}, Damage fee: KES {booking.damage_fee:,.2f}'
            )
            return redirect('all_bookings')
    else:
        form = ReturnForm()

    return render(request, 'bookings/return.html', {
        'booking': booking,
        'form': form,
        'calculated_late_fee': booking.calculate_late_fee(),
    })


@login_required
def cancel_booking(request, pk):
    """Cancel a pending or confirmed booking."""
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    if booking.status not in ('pending', 'confirmed'):
        messages.error(request, 'Only pending or confirmed bookings can be cancelled.')
        return redirect('booking_detail', pk=pk)

    if request.method == 'POST':
        booking.cancel_booking()
        messages.success(request, f'Booking {booking.booking_number} has been cancelled.')
        if request.user.role == 'customer':
            return redirect('my_bookings')
        return redirect('all_bookings')
    return render(request, 'bookings/cancel_confirm.html', {'booking': booking})


@login_required
@staff_required
def overdue_bookings(request):
    """Staff/Admin: view overdue bookings."""
    today = timezone.now().date()
    bookings = Booking.objects.filter(
        status='issued',
        end_date__lt=today,
    )
    # Update status to overdue
    for b in bookings:
        if b.status != 'overdue':
            b.status = Booking.Status.OVERDUE
            b.save()

    overdue = Booking.objects.filter(status='overdue')
    return render(request, 'bookings/overdue.html', {'bookings': overdue})
