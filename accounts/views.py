from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegistrationForm, StaffCreationForm, LoginForm, UserUpdateForm
from .models import User
from .decorators import admin_required


def register_view(request):
    """Customer self-registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Liz Web, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login for all user types."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """View and update profile."""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@admin_required
def manage_users_view(request):
    """Admin: view all users."""
    users = User.objects.all().order_by('-date_joined')
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'accounts/manage_users.html', {
        'users': users,
        'role_filter': role_filter,
    })


@login_required
@admin_required
def create_staff_view(request):
    """Admin: create a staff or admin user."""
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'{user.get_role_display()} account created for {user.username}.')
            return redirect('manage_users')
    else:
        form = StaffCreationForm()
    return render(request, 'accounts/create_staff.html', {'form': form})


@login_required
@admin_required
def toggle_user_active(request, pk):
    """Admin: activate/deactivate a user."""
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    else:
        messages.error(request, 'You cannot deactivate your own account.')
    return redirect('manage_users')
