from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.payment_page, name='booking_payment'),
    # M-Pesa real STK Push
    path('<int:pk>/mpesa/initiate/', views.initiate_mpesa, name='initiate_mpesa'),
    path('<int:pk>/mpesa/status/', views.check_mpesa_status, name='check_mpesa_status'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    # Card
    path('<int:pk>/card/', views.process_card, name='process_card'),
    # History & Reports
    path('history/', views.payment_history, name='payment_history'),
    path('finance-report/', views.finance_report, name='finance_report'),
]
