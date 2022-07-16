# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordResetForm, SetPasswordForm, PasswordChangeForm
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ),
        label='Emailアドレス'
        )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
class VoltPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ),
        label='新しいパスワード'
        )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ),
        label='新しいパスワードの確認'
        )

class VoltPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "john@company.com",
                "class": "form-control"
            }
        ),
        label='Emailアドレス'
        )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class EmailChangeForm(forms.ModelForm):
    """メールアドレス変更フォーム"""

    class Meta:
        model = User
        fields = ('email',)
        
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "john@company.com",
                "class": "form-control"
            }
        ),
        label='Emailアドレス'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

class VoltPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="古いパスワード",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password', 
            "placeholder": "Old Password",
            'autofocus': True,
            "class": "form-control"
            }),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "New Password",
                "class": "form-control"
            }
        ),
        label='新しいパスワード'
        )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ),
        label='新しいパスワードの確認'
        )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class NicknameForm(forms.Form):
    nick_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "ニックネームを入力",
                "class": "form-control"
            }
        ))
    class Meta:
        model = User
        fields = ('nick_name')
