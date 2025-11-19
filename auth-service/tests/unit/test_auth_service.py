# tests/unit/test_user_models.py

from uuid import uuid4
from datetime import datetime

from pydantic import ValidationError

from app.models.user import UserCreate, UserRead, UserRole


def test_user_create_valid():
    """Корректные данные для регистрации пользователя проходят валидацию."""
    data = UserCreate(
        email="user@example.com",
        phone="+70000000000",
        password="StrongPass123",
    )

    assert data.email == "user@example.com"
    assert data.phone == "+70000000000"
    assert data.password == "StrongPass123"


def test_user_create_invalid_email():
    """Некорректный email должен приводить к ValidationError ещё на уровне схемы."""
    try:
        UserCreate(
            email="not-an-email",
            phone=None,
            password="123456",
        )
    except ValidationError:
        # Это ожидаемое поведение
        assert True
    else:
        assert False, "Ожидался ValidationError для некорректного email"


def test_user_read_from_attributes():
    """
    UserRead сконфигурован с from_attributes=True, поэтому должен корректно
    валидировать ORM-объект (или любой объект с нужными атрибутами).
    """
    fake_user_obj = type(
        "User",
        (),
        {
            "id": uuid4(),
            "email": "user2@example.com",
            "phone": None,
            "is_active": True,
            "is_blocked": False,
            "has_2fa": False,
            "role": UserRole.USER,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    )()

    model = UserRead.model_validate(fake_user_obj)

    assert model.email == "user2@example.com"
    assert model.role == UserRole.USER
    assert model.is_active is True
    assert model.is_blocked is False
