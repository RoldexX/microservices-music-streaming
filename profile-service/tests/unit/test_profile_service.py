# tests/unit/test_profile_service.py

from uuid import uuid4
from datetime import datetime, UTC
from pydantic import ValidationError

from app.models.profile import ProfileCreate, ProfileRead


def test_profile_create_valid():
    """Проверка корректных данных для создания профиля."""
    user_id = uuid4()
    data = ProfileCreate(
        user_id=user_id,
        display_name="test_user",
        region="RU",
    )

    assert data.user_id == user_id
    assert data.display_name == "test_user"
    assert data.region == "RU"


def test_profile_create_missing_fields():
    """Отсутствие обязательных полей должно вызывать ValidationError."""
    try:
        ProfileCreate(
            user_id=None,   # неверное значение
            display_name=None,
            region=None,
        )
    except ValidationError:
        assert True
    else:
        assert False, "Ожидался ValidationError для пустых полей"


def test_profile_read_from_attributes():
    """
    Проверим работу from_attributes=True для ORM-объекта.

    В ProfileRead, судя по ошибке, есть обязательное поле id,
    поэтому добавляем его в фейковый объект.
    """
    fake = type(
        "Profile",
        (),
        {
            "id": uuid4(),  # <-- ВАЖНО: id обязателен
            "user_id": uuid4(),
            "display_name": "Tester",
            "region": "EU",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        },
    )()

    model = ProfileRead.model_validate(fake)

    assert model.id is not None
    assert model.display_name == "Tester"
    assert model.region == "EU"
