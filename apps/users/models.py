from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .avatar import generate_avatar
from .managers import UserManager


def avatar_upload_path(instance, filename):
    return f"avatars/user_{instance.pk}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to=avatar_upload_path, blank=True, null=True)
    about = models.TextField("О себе", blank=True, max_length=256)
    phone = models.CharField("Телефон", max_length=12, blank=True)
    github_url = models.URLField("GitHub", blank=True)

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранное",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.avatar:
            letter = self.name[0] if self.name else "?"
            self.avatar.save(f"avatar_{self.pk}.png", generate_avatar(letter), save=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name
