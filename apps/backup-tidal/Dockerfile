FROM python:3.12.1@sha256:a3d69b8412f7068fd060ccc7e175825713d5a767e1e14753e75bce6f746c8a7e AS venv

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv --copies /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --require-virtualenv --no-deps -r /tmp/requirements.txt

FROM python AS dev

COPY --from=venv /venv /venv

WORKDIR /app
COPY backup_tidal.py backup_tidal.py
COPY lib lib

ENV PATH=/venv/bin:$PATH

FROM dev AS prod

WORKDIR /app

USER nobody

ENTRYPOINT ["/app/backup_tidal.py"]
