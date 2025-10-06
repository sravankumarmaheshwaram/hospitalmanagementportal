from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from . import models

# Role choices for unified form
ROLE_CHOICES = [
    ('doctor', 'Doctor'),
    ('patient', 'Patient'),
    ('admin', 'Admin')
]

# Unified Login Form
class UnifiedLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )

# Unified Signup Form - Simplified with basic details only
class UnifiedSignupForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('doctor', 'Doctor'), ('patient', 'Patient')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))
    
    # Basic fields for both doctors and patients
    address = forms.CharField(
        max_length=40, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address'})
    )
    mobile = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mobile Number'})
    )
    
    # Optional fields
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow existing usernames - we'll handle role checking in the view
        return username

# for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


# #for contact us page
# class ContactusForm(forms.Form):
#     Name = forms.CharField(max_length=30)
#     Email = forms.EmailField()
#     Message = forms.CharField(max_length=500,
#                               widget=forms.Textarea(attrs={'rows': 3, 
#                                                            'cols': 30,
#                                                             'style':'resize:none;' }))


