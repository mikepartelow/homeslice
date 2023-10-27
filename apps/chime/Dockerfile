FROM python AS venv

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv --copies /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --require-virtualenv --no-deps -r /tmp/requirements.txt

FROM python AS dev

COPY --from=venv /venv /venv

WORKDIR /app
COPY chime.py chime.py

ENV PATH=/venv/bin:$PATH

FROM dev AS prod

WORKDIR /app

USER nonroot

ENTRYPOINT ["/app/chime.py"]
