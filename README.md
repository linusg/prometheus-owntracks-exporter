# Prometheus OwnTracks Exporter

> A simple Python HTTP server exporting OwnTracks Recorder stats for Prometheus

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
| `owntracks_users_count` | Total number of users |
| `owntracks_version_info` | OwnTracks Recorder version |
| `owntracks_waypoints_count` | Total number of waypoints |
