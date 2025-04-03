FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:0ddac20e6ed02c16bc5f3881619d4ef959427f2ffbe246db87b375b133523be3 AS dev

WORKDIR /app

ENV VIRTUAL_ENV=/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --link-mode=copy --active

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --link-mode=copy --active

FROM python:3.12-slim@sha256:a866731a6b71c4a194a845d86e06568725e430ed21821d0c52e4efb385cf6c6f AS prod

COPY --from=dev --chown=app:app /venv /venv
ADD ./backup_unifi.py /app/backup_unifi.py
ADD ./lib /app/lib

USER nobody

ENTRYPOINT ["/venv/bin/python", "/app/backup_unifi.py"]





FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:0ddac20e6ed02c16bc5f3881619d4ef959427f2ffbe246db87b375b133523be3 AS dev

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

FROM python:3.12@sha256:4e7024df2f2099e87d0a41893c299230d2a974c3474e681b0996f141951f9817 AS prod

COPY --from=dev --chown=app:app /app/.venv /app/.venv
ADD ./backup_unifi.py /app/backup_unifi.py
ADD ./lib /app/lib

USER nobody

ENTRYPOINT ["/app/.venv/bin/python", "/app/backup_unifi.py"]
