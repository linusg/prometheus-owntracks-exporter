FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y build-essential curl gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app/

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev

COPY main.py metrics.py settings.py /app/

EXPOSE 80

CMD ["python", "/app/main.py"]
