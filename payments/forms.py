from django import forms
from .models import Payment


class MpesaPaymentForm(forms.Form):
    """M-Pesa payment form."""
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '254712345678',
            'pattern': '[0-9]+',
        }),
        help_text='Enter M-Pesa phone number (format: 254XXXXXXXXX)'
    )


class CardPaymentForm(forms.Form):
    """Card payment form (simulated for demo)."""
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '4111 1111 1111 1111',
        })
    )
    expiry = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
        })
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
        })
    )
    card_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on Card',
        })
    )
