# For some additional info regarding the various OwnTracks Recorder
# directories and files see:
# https://github.com/owntracks/recorder/blob/master/doc/STORE.md

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, List, Tuple
from urllib.parse import urljoin

import aiofiles  # type: ignore
import aiohttp

__all__ = [
    "get_cards_count",
    "get_devices_count",
    "get_last_locations_count",
    "get_last_received_timestamp",
    "get_locations_count",
    "get_storagedir_size",
    "get_users_count",
    "get_version_info",
    "get_waypoints_count",
]


def _is_owntracks_json_of_type(json_payload: str, _type: str) -> bool:
    try:
        data = json.loads(json_payload)
        return data["_type"] == _type
    except (json.JSONDecodeError, TypeError, KeyError):
        return False


async def _is_owntracks_json_file_of_type(path: Path, _type: str) -> bool:
    if not path.is_file():
        return False
    async with aiofiles.open(path) as f:
        contents = await f.read()
    return _is_owntracks_json_of_type(contents, _type)


def _subdirs(path: Path) -> List[Path]:
    if not path.is_dir():
        return []
    return [
        child_path
        for child_path in path.iterdir()
        if child_path.is_dir() and not child_path.stem.startswith(".")
    ]


def _subdir_names(path: Path) -> Iterator[str]:
    for dir_path in _subdirs(path):
        yield dir_path.resolve().stem


def _user_device_dirs(path: Path) -> Iterator[Tuple[Path, str, str]]:
    for user in _subdir_names(path):
        for device in _subdir_names(path.joinpath(user)):
            yield path.joinpath(user).joinpath(device), user, device


def _get_directory_size(path: Path) -> int:
    total = 0
    for entry in path.iterdir():
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += _get_directory_size(entry)
    return total


def _csv_row_is_location_data(row: str) -> bool:
    try:
        _, _, json_payload = row.split()
        return _is_owntracks_json_of_type(json_payload, "location")
    except ValueError:
        return False


async def _locations_in_rec_file(rec_file: Path) -> int:
    if not rec_file.is_file():
        return 0
    count = 0
    async with aiofiles.open(rec_file) as f:
        async for line in f:
            if _csv_row_is_location_data(line):
                count += 1
    return count


async def get_cards_count(owntracks_storagedir: Path) -> int:
    cards_dir = owntracks_storagedir.joinpath("cards")
    count = 0
    for user in _subdir_names(cards_dir):
        json_file = cards_dir.joinpath(user).joinpath(f"{user}.json")
        if await _is_owntracks_json_file_of_type(json_file, "card"):
            count += 1
    for user_device_dir, user, device in _user_device_dirs(cards_dir):
        for filename in (f"{user}-{device}.json", f"{user}.json"):
            json_file = user_device_dir.joinpath(filename)
            if await _is_owntracks_json_file_of_type(json_file, "card"):
                count += 1
    return count


async def get_devices_count(owntracks_storagedir: Path) -> int:
    return sum(1 for _ in _user_device_dirs(owntracks_storagedir.joinpath("rec")))


async def get_last_locations_count(owntracks_storagedir: Path) -> int:
    count = 0
    for user_device_dir, user, device in _user_device_dirs(
        owntracks_storagedir.joinpath("last")
    ):
        json_file = user_device_dir.joinpath(f"{user}-{device}.json")
        if await _is_owntracks_json_file_of_type(json_file, "location"):
            count += 1
    return count


async def get_last_received_timestamp(owntracks_storagedir: Path) -> int:
    monitor_file = owntracks_storagedir.joinpath("monitor")
    if not monitor_file.is_file():
        return 0
    try:
        async with aiofiles.open(monitor_file) as f:
            contents = await f.read()
        first_line = contents.splitlines()[0]
        timestamp, _ = first_line.split()
        return int(timestamp)
    except (IndexError, ValueError):
        return 0


async def get_locations_count(owntracks_storagedir: Path) -> int:
    count = 0
    for user_device_dir, _, _ in _user_device_dirs(
        owntracks_storagedir.joinpath("rec")
    ):
        for rec_file in user_device_dir.glob("*.rec"):
            count += await _locations_in_rec_file(rec_file)
    return count


async def get_storagedir_size(owntracks_storagedir: Path) -> int:
    return _get_directory_size(owntracks_storagedir)


async def get_users_count(owntracks_storagedir: Path) -> int:
    return sum(1 for _ in _subdirs(owntracks_storagedir.joinpath("rec")))


async def get_version_info(owntracks_url: str) -> Dict[str, str]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(urljoin(owntracks_url, "api/0/version")) as response:
                data = await response.json()
                return {"version": data["version"], "git": data["git"]}
        except Exception:
            return {"version": "", "git": ""}


async def get_waypoints_count(owntracks_storagedir: Path) -> int:
    count = 0
    for user_device_dir, _, _ in _user_device_dirs(
        owntracks_storagedir.joinpath("waypoints")
    ):
        for json_file in user_device_dir.glob("*.json"):
            if await _is_owntracks_json_file_of_type(json_file, "waypoint"):
                count += 1
    return count
