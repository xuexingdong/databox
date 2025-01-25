FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

WORKDIR /app

RUN mkdir -p logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    rm -rf /root/.cache/pip/*

COPY --chown=appuser:appuser . .

USER appuser
CMD ["scrapy", "crawl", "idiom", "-s", "LOG_LEVEL=ERROR"]