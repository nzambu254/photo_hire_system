from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:equipment_id>/', views.create_booking, name='create_booking'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('all/', views.all_bookings, name='all_bookings'),
    path('<int:pk>/issue/', views.issue_equipment, name='issue_equipment'),
    path('<int:pk>/return/', views.return_equipment, name='return_equipment'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('overdue/', views.overdue_bookings, name='overdue_bookings'),

]
