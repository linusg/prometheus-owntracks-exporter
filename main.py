from __future__ import annotations

import asyncio
import datetime
from functools import partial
from typing import Any, Awaitable, Callable, Union, cast

from prometheus_client import (  # type: ignore
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
    REGISTRY,
    Gauge,
    Info,
    make_asgi_app,
)
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route

from metrics import (
    get_cards_count,
    get_devices_count,
    get_last_locations_count,
    get_last_received_timestamp,
    get_locations_count,
    get_storagedir_size,
    get_users_count,
    get_version_info,
    get_waypoints_count,
)
from settings import DEBUG, OWNTRACKS_STORAGEDIR, OWNTRACKS_URL, UPDATE_INTERVAL

REGISTRY.unregister(GC_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)


UpdateFunction = Callable[[], Awaitable]


class Metric:
    def __init__(
        self,
        cls: Union[Gauge, Info],
        name: str,
        description: str,
        update_function: UpdateFunction,
    ) -> None:
        self.name = name
        self.update_function = update_function
        self.value = cls(f"owntracks_{name}", description)

    async def update(self) -> None:
        new_value = await self.update_function()
        self.set_value(new_value)

    def set_value(self, new_value: Any) -> None:
        if isinstance(self.value, Gauge):
            self.value.set(new_value)
        if isinstance(self.value, Info):
            self.value.info(new_value)


METRICS = {
    name: Metric(cls, name, description, cast(UpdateFunction, update_function))
    for cls, name, description, update_function in [
        (
            Gauge,
            "users_count",
            "Total number of users",
            partial(get_users_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "devices_count",
            "Total number of devices",
            partial(get_devices_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "cards_count",
            "Total number of cards",
            partial(get_cards_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "waypoints_count",
            "Total number of waypoints",
            partial(get_waypoints_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "last_locations_count",
            "Total number of last locations",
            partial(get_last_locations_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "locations_count",
            "Total number of locations",
            partial(get_locations_count, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "last_received_timestamp",
            "Timestamp of the last received message",
            partial(get_last_received_timestamp, OWNTRACKS_STORAGEDIR),
        ),
        (
            Gauge,
            "storagedir_size",
            "Size of the OwnTracks Recorder's storage directory in bytes",
            partial(get_storagedir_size, OWNTRACKS_STORAGEDIR),
        ),
        (
            Info,
            "version",
            "OwnTracks Recorder version",
            partial(get_version_info, str(OWNTRACKS_URL)),
        ),
    ]
}


async def update_metrics() -> None:
    await asyncio.gather(*[metric.update() for metric in METRICS.values()])


async def update_metrics_loop() -> None:
    await asyncio.sleep(UPDATE_INTERVAL)
    while True:
        start = datetime.datetime.now()
        await update_metrics()
        end = datetime.datetime.now()
        duration = (end - start).total_seconds()
        await asyncio.sleep(UPDATE_INTERVAL - duration)


routes = [
    Route("/", endpoint=RedirectResponse(url="/metrics")),
    Mount("/metrics", app=make_asgi_app()),
]
app = Starlette(
    debug=DEBUG,
    routes=routes,
    on_startup=[
        update_metrics,
        partial(asyncio.get_event_loop().create_task, update_metrics_loop()),
    ],
)


def run() -> None:
    import uvicorn  # type: ignore

    from settings import SERVER_HOST, SERVER_PORT

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)


if __name__ == "__main__":
    run()
