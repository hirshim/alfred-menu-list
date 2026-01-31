.PHONY: build clean install test lint format check deps help

WORKFLOW_NAME = alfred-menu-list
WORKFLOW_FILE = $(WORKFLOW_NAME).alfredworkflow
BUILD_DIR = build
DIST_DIR = dist

build: clean
	@echo "Building $(WORKFLOW_FILE)..."
	@mkdir -p $(BUILD_DIR)
	@mkdir -p $(DIST_DIR)
	@cp main.py menu_extractor.py sheet_writer.py $(BUILD_DIR)/
	@cp info.plist $(BUILD_DIR)/
	@test -f icon.png && cp icon.png $(BUILD_DIR)/ || true
	@pip3 install --target=$(BUILD_DIR)/lib gspread google-auth --quiet
	@cd $(BUILD_DIR) && zip -r ../$(DIST_DIR)/$(WORKFLOW_FILE) . \
		-x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*"
	@echo "Created: $(DIST_DIR)/$(WORKFLOW_FILE)"

clean:
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DIST_DIR)

install: build
	@open $(DIST_DIR)/$(WORKFLOW_FILE)
	@echo "Opening workflow in Alfred..."

test:
	@PYTHONPATH=. venv/bin/pytest tests/ -v

lint:
	@venv/bin/flake8 *.py tests/
	@venv/bin/mypy *.py

format:
	@venv/bin/black *.py tests/

check: lint test

deps:
	@pip3 install --target=lib gspread google-auth
	@echo "Dependencies installed to lib/"

help:
	@echo "build   - .alfredworkflowパッケージをビルド"
	@echo "clean   - ビルドディレクトリを削除"
	@echo "install - ビルドしてAlfredにインストール"
	@echo "test    - テスト実行"
	@echo "lint    - flake8 + mypy"
	@echo "format  - Blackでフォーマット"
	@echo "check   - lint + test"
	@echo "deps    - lib/に依存ライブラリをバンドル"
