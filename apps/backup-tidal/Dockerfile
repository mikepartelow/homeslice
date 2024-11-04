FROM python:3.12.7@sha256:b52e97a85736bc3a6bfb081ec3f2a5b828233120b2138080af1761e504b06529 AS venv

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv --copies /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --require-virtualenv --no-deps -r /tmp/requirements.txt

FROM python:3.12.7@sha256:b52e97a85736bc3a6bfb081ec3f2a5b828233120b2138080af1761e504b06529 AS dev

COPY --from=venv /venv /venv

WORKDIR /app
COPY backup_tidal.py backup_tidal.py
COPY lib lib

ENV PATH=/venv/bin:$PATH

FROM dev AS prod

WORKDIR /app

USER nobody

ENTRYPOINT ["/app/backup_tidal.py"]
