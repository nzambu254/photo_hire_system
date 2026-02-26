from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('create-staff/', views.create_staff_view, name='create_staff'),
    path('toggle-user/<int:pk>/', views.toggle_user_active, name='toggle_user'),
]
