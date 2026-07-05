from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ("open", "Открыт"),
        ("closed", "Закрыт"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    status = models.CharField("Статус", max_length=6, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
