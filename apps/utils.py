from django import forms
from django.core.paginator import Paginator

from apps.constants import GITHUB_DOMAIN, PAGE_SIZE


def paginate(queryset, request):
    paginator = Paginator(queryset, PAGE_SIZE)
    return paginator.get_page(request.GET.get("page"))


def validate_github_url(url):
    if url:
        host = url.replace("https://", "").replace("http://", "").split("/")[0]
        if host != GITHUB_DOMAIN:
            raise forms.ValidationError("Ссылка должна вести на github.com")
    return url
