FROM python:3.10-slim

# 安装依赖工具
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

# 安装 poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY pyproject.toml poetry.lock ./
COPY . /app

# 安装依赖（包含 dev 依赖如 pytest）
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["python", "app/main.py", "--mode", "api"]
