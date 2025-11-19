# app/services/profile_client.py
from typing import Any, Dict

import requests

from app.settings import settings


class ProfileClient:
    """
    Синхронный HTTP-клиент для вызова internal API profile-service.
    Ожидаем, что base_url уже включает /api/v1.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.profile_service_base_url).rstrip("/")

    def create_profile_for_new_user(
        self,
        user_id: str,
        email: str,
        default_region: str = "RU",
    ) -> Dict[str, Any] | None:
        url = f"{self.base_url}/internal/profiles"
        display_name = email.split("@")[0]

        payload = {
            "user_id": user_id,
            "display_name": display_name,
            "region": default_region,
        }

        try:
            resp = requests.post(url, json=payload, timeout=3)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            # в учебных целях просто игнорируем
            return None
