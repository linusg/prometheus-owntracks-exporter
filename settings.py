from __future__ import annotations

from pathlib import Path

from starlette.config import Config
from starlette.datastructures import URL

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
OWNTRACKS_STORAGEDIR = config("OWNTRACKS_STORAGEDIR", cast=Path)
OWNTRACKS_URL = config("OWNTRACKS_URL", cast=URL)
UPDATE_INTERVAL = config("UPDATE_INTERVAL", cast=int, default=60)
