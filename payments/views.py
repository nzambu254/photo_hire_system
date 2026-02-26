import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Payment
from .forms import MpesaPaymentForm, CardPaymentForm
from .mpesa import mpesa_api
from bookings.models import Booking
from accounts.decorators import admin_required, staff_required


@login_required
def payment_page(request, pk):
    """Payment page for a booking."""
    booking = get_object_or_404(Booking, pk=pk, status='pending')
    if request.user.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    card_form = CardPaymentForm()

    return render(request, 'payments/payment_page.html', {
        'booking': booking,
        'card_form': card_form,
    })


@login_required
@require_POST
def initiate_mpesa(request, pk):
    """
    AJAX endpoint: Initiate real M-Pesa STK Push.
    Sends actual push notification to customer's phone via Daraja API.
    Returns JSON with checkout_request_id for polling.
    """
    booking = get_object_or_404(Booking, pk=pk, status='pending')
    if request.user.role == 'customer' and booking.customer != request.user:
        return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)

    # Parse phone number from request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    phone_number = data.get('phone_number', '').strip()

    if not phone_number or len(phone_number) < 9:
        return JsonResponse({'success': False, 'message': 'Please enter a valid Safaricom phone number.'})

    # Remove spaces and dashes
    phone_number = phone_number.replace(' ', '').replace('-', '')

    # Normalize to 254 format
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+254'):
        phone_number = phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]

    # Validate format
    if not phone_number.startswith('254') or len(phone_number) != 12:
        return JsonResponse({
            'success': False,
            'message': 'Invalid phone number format. Use 0712345678 or 254712345678.'
        })

    # Call the REAL Daraja API
    result = mpesa_api.initiate_stk_push(
        phone_number=phone_number,
        amount=booking.total_amount,
        account_reference=booking.booking_number,
        description=f'Hire: {booking.equipment.name}',
    )

    if result['success']:
        # Create pending payment record
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.total_amount,
            method='mpesa',
            mpesa_phone=phone_number,
            mpesa_checkout_id=result['checkout_request_id'],
            payment_type='hire',
            status='pending',
        )
        return JsonResponse({
            'success': True,
            'message': result['message'],
            'checkout_request_id': result['checkout_request_id'],
            'payment_id': payment.id,
        })
    else:
        return JsonResponse({
            'success': False,
            'message': result['message'],
        })


@login_required
def check_mpesa_status(request, pk):
    """
    AJAX endpoint: Poll M-Pesa STK Push status.
    Frontend calls this every few seconds to check if customer entered PIN.
    Uses Daraja STK Query API (no callback URL needed for localhost).
    """
    checkout_id = request.GET.get('checkout_request_id', '')
    if not checkout_id:
        return JsonResponse({'success': False, 'pending': False, 'failed': True,
                             'message': 'Missing checkout ID.'})

    # Query Daraja for the transaction status
    result = mpesa_api.query_stk_status(checkout_id)

    if result['success']:
        # Payment confirmed! Update our records
        try:
            payment = Payment.objects.get(
                mpesa_checkout_id=checkout_id,
                status='pending',
            )
            receipt = result.get('receipt_number', f'SB{uuid.uuid4().hex[:10].upper()}')
            payment.mark_completed(receipt=receipt)
        except Payment.DoesNotExist:
            pass

        return JsonResponse({
            'success': True,
            'pending': False,
            'failed': False,
            'message': 'Payment successful!',
            'receipt_number': result.get('receipt_number', ''),
            'redirect_url': f'/bookings/{pk}/',
        })

    elif result.get('failed'):
        # Payment failed/cancelled - update record
        try:
            payment = Payment.objects.get(
                mpesa_checkout_id=checkout_id,
                status='pending',
            )
            payment.status = 'failed'
            payment.notes = result['message']
            payment.save()
        except Payment.DoesNotExist:
            pass

        return JsonResponse({
            'success': False,
            'pending': False,
            'failed': True,
            'message': result['message'],
        })

    else:
        # Still pending - customer hasn't entered PIN yet
        return JsonResponse({
            'success': False,
            'pending': True,
            'failed': False,
            'message': result['message'],
        })


@login_required
def process_card(request, pk):
    """Process card payment (simulated for demo)."""
    booking = get_object_or_404(Booking, pk=pk, status='pending')
    if request.method == 'POST':
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            card_last = form.cleaned_data['card_number'][-4:]
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.total_amount,
                method='card',
                card_last_four=card_last,
                transaction_ref=f'TXN-{uuid.uuid4().hex[:12].upper()}',
                payment_type='hire',
            )
            # Simulate successful card payment
            payment.mark_completed(ref=payment.transaction_ref)
            messages.success(request,
                f'Card payment of KES {booking.total_amount:,.2f} processed! '
                f'Reference: {payment.transaction_ref}'
            )
            return redirect('booking_detail', pk=booking.pk)
    return redirect('booking_payment', pk=pk)


@csrf_exempt
def mpesa_callback(request):
    """
    M-Pesa callback URL for production use.
    In sandbox with localhost, we use polling instead.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            callback = data.get('Body', {}).get('stkCallback', {})
            checkout_id = callback.get('CheckoutRequestID')
            result_code = callback.get('ResultCode')

            if checkout_id and str(result_code) == '0':
                receipt = None
                items = callback.get('CallbackMetadata', {}).get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        receipt = item.get('Value')

                try:
                    payment = Payment.objects.get(
                        mpesa_checkout_id=checkout_id,
                        status='pending',
                    )
                    payment.mark_completed(receipt=receipt or '')
                except Payment.DoesNotExist:
                    pass

        except (json.JSONDecodeError, KeyError):
            pass

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@login_required
def payment_history(request):
    """View payment history."""
    if request.user.role == 'customer':
        payments = Payment.objects.filter(user=request.user)
    else:
        payments = Payment.objects.all()

    method_filter = request.GET.get('method', '')
    if method_filter:
        payments = payments.filter(method=method_filter)

    return render(request, 'payments/history.html', {'payments': payments, 'method_filter': method_filter})


@login_required
@admin_required
def finance_report(request):
    """Admin: financial reports and analytics."""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    all_payments = Payment.objects.filter(status='completed')
    total_revenue = all_payments.aggregate(total=Sum('amount'))['total'] or 0
    month_revenue = all_payments.filter(
        created_at__date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    by_method = all_payments.values('method').annotate(
        total=Sum('amount'), count=Count('id')
    )
    by_type = all_payments.values('payment_type').annotate(
        total=Sum('amount'), count=Count('id')
    )

    monthly_data = []
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        month_total = all_payments.filter(
            created_at__month=month, created_at__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_data.append({'month': f'{year}-{month:02d}', 'total': month_total})

    recent = all_payments.order_by('-created_at')[:20]

    outstanding_late = Booking.objects.filter(status='returned', late_fee__gt=0).aggregate(
        total=Sum('late_fee'))['total'] or 0
    outstanding_damage = Booking.objects.filter(status='returned', damage_fee__gt=0).aggregate(
        total=Sum('damage_fee'))['total'] or 0

    context = {
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'by_method': by_method,
        'by_type': by_type,
        'monthly_data': monthly_data,
        'recent_payments': recent,
        'outstanding_late': outstanding_late,
        'outstanding_damage': outstanding_damage,
        'total_transactions': all_payments.count(),
    }
    return render(request, 'payments/finance_report.html', context)