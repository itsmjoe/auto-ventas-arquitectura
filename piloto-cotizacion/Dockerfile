# --- build stage ---
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# --- runtime stage ---
FROM python:3.12-slim AS runtime
WORKDIR /app

# Usuario no-root por seguridad
RUN useradd --create-home --uid 1000 appuser
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY src ./src

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "cotizacion.main:app", "--host", "0.0.0.0", "--port", "8000"]
