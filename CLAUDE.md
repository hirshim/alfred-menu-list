# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

最前面アプリのメニュー項目（全階層）をAppleScriptで取得し、ショートカットキー情報とともにGoogleスプレッドシートに書き込むAlfred Workflow。

- **Workflow名**: `alfred-menu-list`（プロジェクトフォルダ名と同一）
- **作者**: hirshim
- **配布**: `.alfredworkflow` 形式で GitHub Releases アセット

## Commands

```bash
make test     # テスト実行（venv内のpytestを使用）
make lint     # flake8 + mypy
make format   # Blackでフォーマット
make build    # alfred-menu-list.alfredworkflow を生成
make install  # ビルドしてAlfredにインストール
make check    # lint + test
make deps     # pip3 install --target=lib で依存ライブラリをバンドル
```

テスト環境セットアップ:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

## Architecture

- `main.py`: エントリポイント
- `menu_extractor.py`: AppleScript（System Events）でメニュー項目を再帰取得
- `sheet_writer.py`: gspreadでGoogleスプレッドシートに書き込み

### 動作フロー

Alfred `menu` + Enter → Python起動 → AppleScriptでメニュー取得 → スプレッドシート書き込み → macOS通知

## Key Configuration

- **Alfred設定**: `~/Dropbox/Alfred/Alfred.alfredpreferences/`
- **bundleid**: `com.hirshim.alfred-menu-list`
- **ノード**: `[Keyword "menu"] → [Run Script (Python)]`（引数なし）
- **Python**: `/usr/bin/python3`（macOS標準）
- **依存**: gspread, google-auth（`make deps` で `lib/` にバンドル、`sys.path.insert` で読み込み）
- **認証**: `credentials.json`（サービスアカウントキー、gitignore対象）
- **アイコン**: `icon.png` 512x512px、余白は黒（`#000000`）

## Notes

- `credentials.json`, `lib/`, `venv/`, `build/`, `dist/` は `.gitignore` 対象
- アクセシビリティ権限が必要（システム設定 > プライバシーとセキュリティ > アクセシビリティ）
- linter 設定は `setup.cfg`（flake8 max-line-length=120、mypy ignore_missing_imports=True）

## Docs

| ファイル | 内容 |
| -------- | ---- |
| [docs/PLAN.md](docs/PLAN.md) | 詳細設計（カラム構成、AppleScript AX属性、Alfred ノード構成、Google設定手順、ディレクトリ構成） |
| [docs/TODO.md](docs/TODO.md) | 実装タスクリスト |
| [README.md](README.md) | ユーザー向けセットアップ手順（credentials.json の取得・配置方法を含む） |
| [LICENSE](LICENSE) | MIT ライセンス |
