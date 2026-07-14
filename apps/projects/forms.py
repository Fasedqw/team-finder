from django import forms

from apps.constants import GITHUB_DOMAIN
from apps.utils import validate_github_url
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Описание проекта"}),
            "github_url": forms.URLInput(attrs={"placeholder": f"https://{GITHUB_DOMAIN}/..."}),
        }

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", "").strip())
