from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    """Customer booking form."""

    class Meta:
        model = Booking
        fields = ['equipment', 'start_date', 'end_date', 'notes']
        widgets = {
            'equipment': forms.HiddenInput(),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Any special requirements...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        equipment = cleaned_data.get('equipment')

        if start and end:
            today = timezone.now().date()
            if start < today:
                raise forms.ValidationError('Start date cannot be in the past.')
            if end < start:
                raise forms.ValidationError('End date must be after start date.')
            if (end - start).days > 30:
                raise forms.ValidationError('Maximum hire period is 30 days.')

        if equipment and not equipment.is_available:
            raise forms.ValidationError('This equipment is not currently available.')

        # Check for overlapping bookings
        if equipment and start and end:
            overlapping = Booking.objects.filter(
                equipment=equipment,
                status__in=['confirmed', 'issued'],
                start_date__lte=end,
                end_date__gte=start,
            ).exists()
            if overlapping:
                raise forms.ValidationError('This equipment is already booked for the selected dates.')

        return cleaned_data


class ReturnForm(forms.Form):
    """Staff form for processing equipment return."""
    damage_fee = forms.DecimalField(
        max_digits=10, decimal_places=2, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        help_text='Charge for any equipment damage (KES)'
    )
    damage_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Describe any damage to the equipment...'
        })
    )
