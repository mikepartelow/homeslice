FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:0ddac20e6ed02c16bc5f3881619d4ef959427f2ffbe246db87b375b133523be3 AS dev

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --link-mode=copy

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --link-mode=copy

FROM python:3.12@sha256:4e7024df2f2099e87d0a41893c299230d2a974c3474e681b0996f141951f9817 AS prod

COPY --from=dev --chown=app:app /venv /venv
ADD ./pylmz.py /app/pylmz.py
ADD ./lib /app/lib

USER nobody

ENTRYPOINT ["/venv/bin/python", "/app/pylmz.py"]
