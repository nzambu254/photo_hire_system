from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Equipment, Category
from .forms import EquipmentForm, CategoryForm
from accounts.decorators import admin_required, staff_required


def equipment_list(request):
    """Public: browse all available equipment."""
    items = Equipment.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Filters
    category_id = request.GET.get('category')
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if category_id:
        items = items.filter(category_id=category_id)
    if search:
        items = items.filter(
            Q(name__icontains=search) | Q(brand__icontains=search) |
            Q(description__icontains=search)
        )
    if status_filter:
        items = items.filter(status=status_filter)

    return render(request, 'equipment/list.html', {
        'items': items,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'status_filter': status_filter,
    })


def equipment_detail(request, pk):
    """Public: view equipment details."""
    item = get_object_or_404(Equipment, pk=pk, is_active=True)
    return render(request, 'equipment/detail.html', {'item': item})


@login_required
@admin_required
def equipment_create(request):
    """Admin: add new equipment."""
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment added successfully!')
            return redirect('equipment_manage')
    else:
        form = EquipmentForm()
    return render(request, 'equipment/form.html', {'form': form, 'title': 'Add Equipment'})


@login_required
@admin_required
def equipment_edit(request, pk):
    """Admin: edit equipment."""
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment updated successfully!')
            return redirect('equipment_manage')
    else:
        form = EquipmentForm(instance=item)
    return render(request, 'equipment/form.html', {'form': form, 'title': 'Edit Equipment'})


@login_required
@admin_required
def equipment_delete(request, pk):
    """Admin: deactivate equipment."""
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        item.is_active = False
        item.save()
        messages.success(request, f'{item.name} has been removed from catalog.')
        return redirect('equipment_manage')
    return render(request, 'equipment/confirm_delete.html', {'item': item})


@login_required
@staff_required
def equipment_manage(request):
    """Staff/Admin: manage all equipment."""
    items = Equipment.objects.all()
    categories = Category.objects.all()
    return render(request, 'equipment/manage.html', {'items': items, 'categories': categories})


@login_required
@admin_required
def category_manage(request):
    """Admin: manage categories."""
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_manage')
    else:
        form = CategoryForm()
    return render(request, 'equipment/categories.html', {'categories': categories, 'form': form})


@login_required
@admin_required
def category_delete(request, pk):
    """Admin: delete category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        if category.equipment_set.exists():
            messages.error(request, 'Cannot delete category with equipment. Move equipment first.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.name}" deleted.')
    return redirect('category_manage')
