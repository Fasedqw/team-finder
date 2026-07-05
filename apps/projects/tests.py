from django.test import TestCase
from django.urls import reverse

from apps.users.models import User

from .models import Project


class ProjectTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@mail.ru", password="pass12345", name="Иван", surname="Петров"
        )
        self.other = User.objects.create_user(
            email="other@mail.ru", password="pass12345", name="Мария", surname="Иванова"
        )
        self.project = Project.objects.create(
            owner=self.owner, name="Тестовый проект", description="Описание"
        )

    def test_project_list_anonymous(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)

    def test_create_project_requires_login(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)

    def test_create_project(self):
        self.client.login(email="owner@mail.ru", password="pass12345")
        response = self.client.post(reverse("projects:create"), {
            "name": "Новый проект", "description": "", "github_url": "", "status": "open",
        })
        project = Project.objects.get(name="Новый проект")
        self.assertRedirects(response, reverse("projects:detail", args=[project.pk]))
        self.assertEqual(project.owner, self.owner)
        self.assertIn(self.owner, project.participants.all())

    def test_edit_project_forbidden(self):
        self.client.login(email="other@mail.ru", password="pass12345")
        response = self.client.get(reverse("projects:edit", args=[self.project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_edit_project_ok(self):
        self.client.login(email="owner@mail.ru", password="pass12345")
        self.client.post(reverse("projects:edit", args=[self.project.pk]), {
            "name": "Обновлено", "description": "", "github_url": "", "status": "open",
        })
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Обновлено")

    def test_toggle_favorite(self):
        self.client.login(email="other@mail.ru", password="pass12345")
        url = reverse("projects:toggle-favorite", args=[self.project.pk])
        self.client.post(url)
        self.assertIn(self.project, self.other.favorites.all())
        self.client.post(url)
        self.assertNotIn(self.project, self.other.favorites.all())

    def test_toggle_participate(self):
        self.client.login(email="other@mail.ru", password="pass12345")
        url = reverse("projects:toggle-participate", args=[self.project.pk])
        r = self.client.post(url)
        self.assertTrue(r.json()["participant"])
        r = self.client.post(url)
        self.assertFalse(r.json()["participant"])

    def test_owner_cannot_participate(self):
        self.client.login(email="owner@mail.ru", password="pass12345")
        r = self.client.post(reverse("projects:toggle-participate", args=[self.project.pk]))
        self.assertEqual(r.status_code, 400)

    def test_complete_project(self):
        self.client.login(email="owner@mail.ru", password="pass12345")
        r = self.client.post(reverse("projects:complete", args=[self.project.pk]))
        self.assertEqual(r.json()["project_status"], "closed")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_delete_project(self):
        self.client.login(email="owner@mail.ru", password="pass12345")
        self.client.post(reverse("projects:delete", args=[self.project.pk]))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_delete_project_forbidden(self):
        self.client.login(email="other@mail.ru", password="pass12345")
        r = self.client.post(reverse("projects:delete", args=[self.project.pk]))
        self.assertEqual(r.status_code, 403)
