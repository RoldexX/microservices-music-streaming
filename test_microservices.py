#!/usr/bin/env python3
"""
test_microservices.py

Сценарий:
1. Регистрация пользователя в auth-service.
2. Проверка, что profile-service создал профиль.
3. Создание альбома и трека в catalog-service.
4. Создание плейлиста и добавление трека в библиотеке (search-library-service),
   что проверяет HTTP-вызов в catalog-service и публикацию событий в RabbitMQ.
5. Запуск воспроизведения и остановка трека в playback-service,
   что снова проверяет HTTP-вызов в catalog-service и события playback.*.
6. Проверка, что notifications-service получил события через RabbitMQ
   и сохранил уведомления для пользователя.
"""

import time
import uuid
from typing import Any, Dict

import requests


BASE_AUTH = "http://localhost:8000/api/v1"
BASE_PROFILE = "http://localhost:8001/api/v1"
BASE_CATALOG = "http://localhost:8002/api/v1"
BASE_SEARCH_LIB = "http://localhost:8003/api/v1"
BASE_NOTIFICATIONS = "http://localhost:8004/api/v1"
BASE_PLAYBACK = "http://localhost:8005/api/v1"


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def assert_status(resp: requests.Response, expected: int = 200) -> Dict[str, Any]:
    if resp.status_code != expected:
        print(f"URL: {resp.request.method} {resp.url}")
        print("Status:", resp.status_code)
        print("Response:", resp.text)
        raise AssertionError(f"Expected status {expected}, got {resp.status_code}")
    try:
        return resp.json()
    except Exception:
        print("Non-JSON response:", resp.text)
        raise


def main() -> None:
    # ------------------------------------------------------------------ #
    # 1. Регистрация пользователя (auth-service)                         #
    # ------------------------------------------------------------------ #
    print_header("1. Регистрация пользователя в auth-service")

    unique_suffix = uuid.uuid4().hex[:8]
    email = f"test_{unique_suffix}@example.com"
    password = "TestPassword123!"
    phone = "+70000000000"

    resp = requests.post(
        f"{BASE_AUTH}/auth/register",
        json={
            "email": email,
            "phone": phone,
            "password": password,
        },
        timeout=5,
    )
    data = assert_status(resp, expected=200)
    user_id = data["user_id"]
    print(f"Зарегистрирован пользователь: user_id={user_id}, email={email}")

    # Авторизация (заодно проверяем /auth/login)
    resp = requests.post(
        f"{BASE_AUTH}/auth/login",
        json={
            "email": email,
            "password": password,
            "device_id": "test-device",
        },
        timeout=5,
    )
    login_data = assert_status(resp, expected=200)
    print("Получены токены:", login_data)

    # Дадим немного времени profile-service и notifications-worker
    time.sleep(1.5)

    # ------------------------------------------------------------------ #
    # 2. Проверка профиля (profile-service)                              #
    # ------------------------------------------------------------------ #
    print_header("2. Проверка создания профиля в profile-service")

    resp = requests.get(
        f"{BASE_PROFILE}/profiles/me",
        params={"user_id": user_id},
        timeout=5,
    )
    profile = assert_status(resp, expected=200)
    print("Профиль пользователя:", profile)

    assert profile["user_id"] == user_id
    assert profile["display_name"].startswith("test_"), "display_name не соответствует ожиданиям"

    # ------------------------------------------------------------------ #
    # 3. Создание альбома и трека (catalog-service)                      #
    # ------------------------------------------------------------------ #
    print_header("3. Создание альбома и трека в catalog-service")

    # Создаём альбом
    resp = requests.post(
        f"{BASE_CATALOG}/albums",
        json={
            "title": "Test Album",
            "artist_name": "Test Artist",
            "release_date": None,
            "cover_url": None,
        },
        timeout=5,
    )
    album = assert_status(resp, expected=200)
    album_id = album["id"]
    print("Создан альбом:", album)

    # Публикуем альбом
    resp = requests.post(
        f"{BASE_CATALOG}/albums/{album_id}:publish",
        timeout=5,
    )
    album_published = assert_status(resp, expected=200)
    print("Альбом опубликован:", album_published)

    # Создаём трек
    resp = requests.post(
        f"{BASE_CATALOG}/tracks/albums/{album_id}",
        json={
            "title": "Test Track",
            "duration_sec": 180,
            "file_path": "test/track/path.mp3",
        },
        timeout=5,
    )
    track = assert_status(resp, expected=200)
    track_id = track["id"]
    print("Создан трек:", track)

    # Публикуем трек
    resp = requests.post(
        f"{BASE_CATALOG}/tracks/{track_id}:publish",
        timeout=5,
    )
    track_published = assert_status(resp, expected=200)
    print("Трек опубликован:", track_published)

    # ------------------------------------------------------------------ #
    # 4. Библиотека: плейлист и добавление трека (search-library-service)#
    # ------------------------------------------------------------------ #
    print_header("4. Работа библиотеки в search-library-service")

    # Создаем плейлист
    resp = requests.post(
        f"{BASE_SEARCH_LIB}/me/playlists",
        params={"owner_id": user_id},
        json={
            "title": "My Test Playlist",
            "is_public": False,
        },
        timeout=5,
    )
    playlist = assert_status(resp, expected=200)
    playlist_id = playlist["id"]
    print("Создан плейлист:", playlist)

    # Добавляем трек в плейлист (тут должен быть HTTP-вызов в catalog-service)
    resp = requests.post(
        f"{BASE_SEARCH_LIB}/me/playlists/{playlist_id}:add-track",
        params={"owner_id": user_id},
        json={
            "track_id": track_id,
            "position": None,
        },
        timeout=5,
    )
    add_track_result = assert_status(resp, expected=200)
    print("Результат добавления трека в плейлист:", add_track_result)

    # Добавляем трек в избранное
    resp = requests.post(
        f"{BASE_SEARCH_LIB}/me/favorites/tracks",
        params={"owner_id": user_id},
        json={"track_id": track_id},
        timeout=5,
    )
    favorite = assert_status(resp, expected=200)
    print("Трек добавлен в избранное:", favorite)

    # ------------------------------------------------------------------ #
    # 5. Воспроизведение (playback-service)                              #
    # ------------------------------------------------------------------ #
    print_header("5. Тест playback-service")

    # Старт воспроизведения
    resp = requests.post(
        f"{BASE_PLAYBACK}/playback/start",
        json={
            "user_id": user_id,
            "track_id": track_id,
            "context_type": "playlist",
            "context_id": playlist_id,
            "volume": 70,
        },
        timeout=5,
    )
    session = assert_status(resp, expected=200)
    session_id = session["id"]
    print("Старт воспроизведения, сессия:", session)

    # Пауза
    resp = requests.post(
        f"{BASE_PLAYBACK}/playback/{session_id}:pause",
        timeout=5,
    )
    session_paused = assert_status(resp, expected=200)
    print("Сессия после паузы:", session_paused)

    # Резюм
    resp = requests.post(
        f"{BASE_PLAYBACK}/playback/{session_id}:resume",
        timeout=5,
    )
    session_resumed = assert_status(resp, expected=200)
    print("Сессия после resume:", session_resumed)

    # Стоп (генерирует playback.track.finished)
    resp = requests.post(
        f"{BASE_PLAYBACK}/playback/{session_id}:stop",
        timeout=5,
    )
    session_stopped = assert_status(resp, expected=200)
    print("Сессия после stop:", session_stopped)

    # ------------------------------------------------------------------ #
    # 6. Проверка уведомлений (notifications-service)                    #
    # ------------------------------------------------------------------ #
    print_header("6. Проверка уведомлений в notifications-service")

    # Дадим воркеру время прочитать очередь RabbitMQ и записать в БД
    max_wait_sec = 10
    deadline = time.time() + max_wait_sec
    notifications: list[dict[str, Any]] = []

    while time.time() < deadline:
        resp = requests.get(
            f"{BASE_NOTIFICATIONS}/me/notifications",
            params={"user_id": user_id, "include_read": True},
            timeout=5,
        )
        notifications = assert_status(resp, expected=200)
        if notifications:
            break
        print("Уведомлений пока нет, ждём ещё 1 сек...", flush=True)
        time.sleep(1)

    print(f"Найдено уведомлений для user_id={user_id}: {len(notifications)}")
    for n in notifications:
        print(f"- [{n['created_at']}] {n['title']}: {n['body']}")

    if len(notifications) < 2:
        raise AssertionError("Ожидалось минимум 2 уведомления, получили меньше.")


if __name__ == "__main__":
    main()
