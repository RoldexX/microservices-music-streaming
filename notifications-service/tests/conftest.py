# tests/conftest.py
import os
import sys

# Абсолютный путь до корня сервиса (где лежит папка app)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ROOT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
