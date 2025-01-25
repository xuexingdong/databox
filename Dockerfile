FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# 使用 Poetry 安装依赖
RUN poetry install --no-dev --no-interaction --no-ansi && \
    poetry cache clear pypi --all

RUN pip install poetry

COPY --chown=appuser:appuser . .

USER appuser
CMD ["scrapy", "crawl", "land", "-s", "LOG_LEVEL=ERROR"]