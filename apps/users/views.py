from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import update_session_auth_hash
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.constants import PAGE_SIZE
from .forms import LoginForm, ProfileEditForm, RegisterForm
from .models import User


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        return redirect("projects:list")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("users:login")


def user_detail(request, pk):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects"), pk=pk
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён")
        return redirect("users:detail", pk=request.user.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль изменён")
        return redirect("users:detail", pk=request.user.pk)
    return render(request, "users/change_password.html", {"form": form})


def participants_list(request):
    users_qs = User.objects.order_by("id")
    active_filter = request.GET.get("filter")

    if active_filter and request.user.is_authenticated:
        me = request.user
        if active_filter == "owners-of-favorite-projects":
            owner_ids = me.favorites.values_list("owner_id", flat=True)
            users_qs = users_qs.filter(id__in=owner_ids)
        elif active_filter == "owners-of-participating-projects":
            owner_ids = me.participated_projects.values_list("owner_id", flat=True)
            users_qs = users_qs.filter(id__in=owner_ids)
        elif active_filter == "interested-in-my-projects":
            user_ids = User.objects.filter(
                favorites__owner=me
            ).values_list("id", flat=True)
            users_qs = users_qs.filter(id__in=user_ids).exclude(id=me.id)
        elif active_filter == "participants-of-my-projects":
            user_ids = User.objects.filter(
                participated_projects__owner=me
            ).values_list("id", flat=True)
            users_qs = users_qs.filter(id__in=user_ids).exclude(id=me.id)
        else:
            active_filter = None

    users_qs = users_qs.distinct()
    paginator = Paginator(users_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "users/participants.html", {
        "participants": page_obj,
        "page_obj": page_obj,
        "active_filter": active_filter,
    })
