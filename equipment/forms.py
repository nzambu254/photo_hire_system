from django import forms
from .models import Equipment, Category


class EquipmentForm(forms.ModelForm):
    """Form for creating/editing equipment."""

    class Meta:
        model = Equipment
        fields = ['category', 'name', 'description', 'brand', 'model_number',
                  'serial_number', 'daily_rate', 'replacement_value', 'status',
                  'image', 'image_url', 'condition_notes', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Equipment Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model Number'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial Number'}),
            'daily_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Daily Rate (KES)'}),
            'replacement_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Replacement Value (KES)'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
            'condition_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""

    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-camera'}),
        }
