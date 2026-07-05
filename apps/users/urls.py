from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("list/", views.participants_list, name="list"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("edit-profile/", views.edit_profile, name="edit-profile"),
    path("change-password/", views.change_password, name="change-password"),
    path("<int:pk>", views.user_detail, name="detail"),
    # в шаблонах ссылка на профиль встречается то со слешем на конце, то без —
    # чтобы не городить редиректы, просто вешаем второй путь на тот же view
    path("<int:pk>/", views.user_detail),
]
