FROM python:3.10-slim

# 安装 Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

# 设置工作目录
WORKDIR /app

# 复制项目依赖配置
COPY pyproject.toml poetry.lock ./

# 安装依赖（不安装 dev 依赖、不安装当前项目）
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-dev

# 复制项目代码
COPY . .

# 设置默认执行命令
CMD ["python", "main.py"]
