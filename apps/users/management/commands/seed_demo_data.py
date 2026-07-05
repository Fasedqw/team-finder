from django.core.management.base import BaseCommand

from apps.projects.models import Project
from apps.users.models import User


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты"

    def handle(self, *args, **options):
        users_data = [
            {
                "email": "maria@yandex.ru",
                "password": "password",
                "name": "Мария",
                "surname": "Иванова",
                "about": "Frontend-разработчик, люблю React.",
                "phone": "+79000000001",
                "github_url": "https://github.com/maria",
            },
            {
                "email": "ivan@yandex.ru",
                "password": "password",
                "name": "Иван",
                "surname": "Петров",
                "about": "Backend на Python/Django.",
                "phone": "+79000000002",
                "github_url": "https://github.com/ivan",
            },
            {
                "email": "olga@yandex.ru",
                "password": "password",
                "name": "Ольга",
                "surname": "Смирнова",
                "about": "UX/UI дизайнер.",
                "phone": "+79000000003",
                "github_url": "https://github.com/olga",
            },
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={k: v for k, v in data.items() if k not in ("email", "password")},
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан: {user.email}"))
            else:
                self.stdout.write(f"Уже есть: {user.email}")
            users.append(user)

        projects_data = [
            {
                "owner": users[0],
                "name": "TeamFinder UI Kit",
                "description": "Библиотека React-компонентов для платформы.",
                "github_url": "https://github.com/maria/teamfinder-ui",
            },
            {
                "owner": users[1],
                "name": "API трекера привычек",
                "description": "Django REST API для мобильного приложения.",
                "github_url": "https://github.com/ivan/habits-api",
            },
            {
                "owner": users[2],
                "name": "Редизайн лендинга",
                "description": "Ищу разработчика для вёрстки макета.",
                "github_url": "",
            },
        ]

        for data in projects_data:
            project, created = Project.objects.get_or_create(
                owner=data["owner"],
                name=data["name"],
                defaults={"description": data["description"], "github_url": data["github_url"]},
            )
            if created:
                project.participants.add(data["owner"])
                self.stdout.write(self.style.SUCCESS(f"Создан проект: {project.name}"))

        maria, ivan, olga = users
        ivan_project = Project.objects.filter(owner=ivan).first()
        olga_project = Project.objects.filter(owner=olga).first()
        if ivan_project:
            maria.favorites.add(ivan_project)
            ivan_project.participants.add(olga)
        if olga_project:
            ivan.favorites.add(olga_project)

        self.stdout.write(self.style.SUCCESS("Готово."))
