# Константы проекта — все "магические числа" и строки собраны здесь

from http import HTTPStatus

# Пагинация
PAGE_SIZE = 12

# Статусы проектов
PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"

# HTTP статусы (используем стандартные константы Python)
HTTP_200_OK = HTTPStatus.OK
HTTP_400_BAD_REQUEST = HTTPStatus.BAD_REQUEST
HTTP_403_FORBIDDEN = HTTPStatus.FORBIDDEN

# Валидация телефона
PHONE_REGEX = r"^\+7\d{10}$"
GITHUB_DOMAIN = "github.com"

# Размеры полей (дублируют модели — для виджетов форм)
ABOUT_MAX_LENGTH = 256
NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
