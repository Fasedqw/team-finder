from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.constants import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN
from apps.utils import paginate
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = Project.objects.select_related("owner")
    page_obj = paginate(projects, request)
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
    form = ProjectForm(request.POST or None)
    if not form.is_valid():
        return render(request, "projects/create-project.html", {"form": form, "is_edit": False})
    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    messages.success(request, "Проект опубликован")
    return redirect("projects:detail", pk=project.pk)


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Редактировать может только автор")
    form = ProjectForm(request.POST or None, instance=project)
    if not form.is_valid():
        return render(request, "projects/create-project.html", {
            "form": form, "is_edit": True, "project": project,
        })
    form.save()
    messages.success(request, "Изменения сохранены")
    return redirect("projects:detail", pk=project.pk)


@login_required
@require_POST
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Удалить может только автор")
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
    favorited = request.user.favorites.filter(pk=project.pk).exists()
    if favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not favorited})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner == request.user:
        return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)
    participating = project.participants.filter(pk=request.user.pk).exists()
    if participating:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not participating})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)
    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже закрыт"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})
