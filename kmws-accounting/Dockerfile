FROM python:3.10-slim AS builder

RUN python -m venv .venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /app
COPY . .
RUN pip install .

FROM python:3.10-slim

COPY --from=builder /.venv .venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /app
EXPOSE 8000
ENTRYPOINT [ "uvicorn", "kmws_accounting:app", "--host=0.0.0.0", "--port=8000"]
