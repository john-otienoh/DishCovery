# forms.py

from django import forms
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm, ResetPasswordKeyForm, AddEmailForm

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email',
            'id': 'id_login',
            'required': True
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
            'id': 'id_password',
            'required': True
        })

        self.fields['remember'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember'
        })

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'id': 'id_username'
        })

        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email',
            'id': 'id_email',
            'required': True
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create Password',
            'id': 'id_password1',
            'required': True
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'id_password2',
            'required': True
        })

class CustomPasswordResetForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-3 py-2 rounded-md bg-gray-700 text-gray-300 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Your Email'
        })



class CustomSetPasswordForm(ResetPasswordKeyForm):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password',
            'class': 'w-full bg-gray-700 text-white px-3 py-2 rounded-md'
        })
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'w-full bg-gray-700 text-white px-3 py-2 rounded-md'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'autofocus': 'true'
        })


class CustomAddEmailForm(AddEmailForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'input input-primary block w-full mt-1 text-lg rounded border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Your Email'
            }
        ),
        label='Email Address'
    )
    