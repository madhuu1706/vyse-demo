FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv pip install --system -e .
COPY . .
EXPOSE 8000
# Shell form so ${PORT} is expanded at runtime; defaults to 8000 locally.
CMD uvicorn vyse_api.main:app --host 0.0.0.0 --port ${PORT:-8000}
