from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project

from .models import User


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@mail.ru", password="pass12345", name="Иван", surname="Иванов"
        )
        self.assertTrue(user.check_password("pass12345"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@mail.ru", password="pass12345")
        self.assertTrue(admin.is_staff)


class RegisterTest(TestCase):
    def test_register_ok(self):
        response = self.client.post(reverse("users:register"), {
            "name": "Мария", "surname": "Иванова",
            "email": "maria@mail.ru", "password": "password123",
        })
        self.assertRedirects(response, reverse("projects:list"))
        self.assertTrue(User.objects.filter(email="maria@mail.ru").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="dup@mail.ru", password="pass", name="А", surname="Б")
        response = self.client.post(reverse("users:register"), {
            "name": "В", "surname": "Г", "email": "dup@mail.ru", "password": "pass12345",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email="dup@mail.ru").count(), 1)

    def test_login_ok(self):
        User.objects.create_user(email="u@mail.ru", password="pass12345", name="А", surname="Б")
        response = self.client.post(reverse("users:login"), {
            "email": "u@mail.ru", "password": "pass12345",
        })
        self.assertRedirects(response, reverse("projects:list"))

    def test_login_wrong_password(self):
        User.objects.create_user(email="u2@mail.ru", password="pass12345", name="А", surname="Б")
        response = self.client.post(reverse("users:login"), {
            "email": "u2@mail.ru", "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="me@mail.ru", password="pass12345", name="Мария", surname="Иванова"
        )
        self.other = User.objects.create_user(
            email="other@mail.ru", password="pass12345", name="Иван", surname="Петров"
        )
        self.client.login(email="me@mail.ru", password="pass12345")

    def test_edit_profile(self):
        response = self.client.post(reverse("users:edit-profile"), {
            "name": "Новое", "surname": "Имя", "about": "", "phone": "", "github_url": "",
        })
        self.assertRedirects(response, reverse("users:detail", args=[self.user.pk]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Новое")

    def test_filter_owners_of_favorites(self):
        project = Project.objects.create(owner=self.other, name="Проект", description="")
        self.user.favorites.add(project)
        response = self.client.get(reverse("users:list"), {"filter": "owners-of-favorite-projects"})
        self.assertEqual(response.status_code, 200)
        participants = list(response.context["participants"])
        self.assertIn(self.other, participants)
