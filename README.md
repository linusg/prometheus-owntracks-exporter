# Prometheus OwnTracks Exporter

> A simple Python HTTP server exporting OwnTracks Recorder stats for Prometheus

[![Build (Docker)](https://github.com/linusg/prometheus-owntracks-exporter/workflows/Build%20%28Docker%29/badge.svg)](https://github.com/linusg/prometheus-owntracks-exporter/actions?query=workflow%3A%22Build+%28Docker%29%22+branch%3Amaster)
[![Lint](https://github.com/linusg/prometheus-owntracks-exporter/workflows/Lint/badge.svg)](https://github.com/linusg/prometheus-owntracks-exporter/actions?query=workflow%3ALint+branch%3Amaster)
[![Docker Pulls](https://img.shields.io/docker/pulls/linusgroh/prometheus-owntracks-exporter)](https://hub.docker.com/r/linusgroh/prometheus-owntracks-exporter)
[![License](https://img.shields.io/github/license/linusg/prometheus-owntracks-exporter?color=d63e97)](https://github.com/linusg/prometheus-owntracks-exporter/blob/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/ambv/black)

## Installation

### Docker

Pre-built Docker images are available on Docker Hub: [`linusgroh/prometheus-owntracks-exporter`](https://hub.docker.com/r/linusgroh/prometheus-owntracks-exporter)

```console
docker run -d \
  -v "/path/to/owntracks/storage:/owntracks" \
  -e OWNTRACKS_STORAGEDIR="/owntracks" \
  -e OWNTRACKS_URL="http://owntracks-recorder:8083" \
  linusgroh/prometheus-owntracks-exporter
```

### Docker Compose

```yaml
services:
  owntracks-recorder:
    ...

  prometheus:
    ...

  prometheus-owntracks-exporter:
    image: linusgroh/prometheus-owntracks-exporter
    depends_on:
      - prometheus
    volumes:
      - /path/to/owntracks/storage:/owntracks
    environment:
      OWNTRACKS_STORAGEDIR: /owntracks
      OWNTRACKS_URL: http://owntracks-recorder:8083
```

### Manually

```console
poetry install --no-root --no-dev
poetry run uvicorn main:app
```

### Development

```console
poetry install --no-root
poetry run uvicorn main:app --reload
```

## Configuration

Configuration is done via environment variables (or by adding a `.env` file).

| Name | Description | Default |
| :--- | :---------- | :------ |
| `DEBUG` | Run the underlying Starlette ASGI app in debug mode | `False` |
| `OWNTRACKS_STORAGEDIR` | Path to the OwnTracks Recorder storage directory (`OTR_STORAGEDIR`, `--storagedir`)| |
| `OWNTRACKS_URL` | Base URL to the OwnTracks Recorder's HTTP API (without `/api/...`) | |
| `UPDATE_INTERVAL` | Interval in which the metrics are updated (in seconds) | `60` |

When using the Docker image a few more environment variables are available (inherited) - see [here](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).

### `prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'owntracks'
    static_configs:
      - targets: ['prometheus-owntracks-exporter:80']
```

## Metrics

| Name | Description |
|------|-------------|
| `owntracks_cards_count` | Total number of cards |
| `owntracks_devices_count` | Total number of devices |
| `owntracks_last_locations_count` | Total number of last locations |
| `owntracks_last_received_timestamp` | Timestamp of the last received message |
| `owntracks_locations_count` | Total number of locations |
| `owntracks_storagedir_size` | Size of the OwnTracks Recorder's storage directory in bytes |
| `owntracks_users_count` | Total number of users |
| `owntracks_version_info` | OwnTracks Recorder version |
| `owntracks_waypoints_count` | Total number of waypoints |

## Grafana

A simple Grafana dashboard is available in [`grafana/owntracks.json`](grafana/owntracks.json).
