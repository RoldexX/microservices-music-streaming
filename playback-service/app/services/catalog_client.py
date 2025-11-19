# app/services/catalog_client.py
from typing import Any, Dict

import requests

from app.settings import settings


class CatalogClient:
    """
    Синхронный клиент к catalog-service.
    Нужен, чтобы убедиться, что трек существует перед стартом воспроизведения.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.catalog_service_base_url

    def get_track(self, track_id: str) -> Dict[str, Any] | None:
        url = f"{self.base_url}/api/v1/tracks/{track_id}"
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
