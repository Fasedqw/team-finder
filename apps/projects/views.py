from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project

PAGE_SIZE = 12


def project_list(request):
    projects = Project.objects.select_related("owner")
    paginator = Paginator(projects, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/project_list.html", {
        "projects": page_obj,
        "page_obj": page_obj,
    })


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"), pk=pk
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            messages.success(request, "Проект опубликован")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(initial={"status": "open"})
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {
        "form": form, "is_edit": True, "project": project,
    })


@login_required
@require_POST
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden()
    project.delete()
    messages.success(request, "Проект удалён")
    return redirect("projects:list")


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner")
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error"}, status=400)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=403)
    if project.status != "open":
        return JsonResponse({"status": "error", "message": "Проект уже закрыт"}, status=400)
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})
