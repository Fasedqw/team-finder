import re

from django import forms
from django.contrib.auth import authenticate

from apps.constants import PHONE_REGEX
from apps.utils import validate_github_url
from .models import User


def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]
    return phone


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
        min_length=8,
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned

    def get_user(self):
        return self.user_cache


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "name", "surname", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        normalized = normalize_phone(phone)
        if not re.match(PHONE_REGEX, normalized):
            raise forms.ValidationError("Формат: 8XXXXXXXXXX или +7XXXXXXXXXX")
        qs = User.objects.filter(phone=normalized)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Такой номер уже используется")
        return normalized

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", "").strip())
