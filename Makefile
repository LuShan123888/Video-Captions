.PHONY: help install build publish clean test lint format dev

# 默认目标
help:
	@echo "Bilibili-Captions Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make install     - 本地安装包"
	@echo "  make build       - 构建发布包"
	@echo "  make publish     - 发布到 PyPI"
	@echo "  make clean       - 清理构建文件"
	@echo "  make test        - 运行测试"
	@echo "  make lint        - 代码检查"
	@echo "  make format      - 代码格式化"
	@echo "  make dev         - 安装开发依赖"

# 本地安装
install:
	uv sync

# 构建发布包
build:
	rm -rf dist/
	uv build

# 发布到 PyPI
publish: build
	UV_PUBLISH_TOKEN="${UV_PUBLISH_TOKEN}" uv publish

# 清理构建文件
clean:
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 运行测试
test:
	uv run pytest tests/

# 代码检查
lint:
	uv run ruff check .

# 代码格式化
format:
	uv run ruff format .

# 安装开发依赖
dev:
	uv sync --dev
