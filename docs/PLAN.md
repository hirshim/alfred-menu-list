# PLAN.md

`alfred-menu-list` の詳細設計。

## スプレッドシートのカラム構成

各メニュー項目を1行として、階層ごとにカラムを分割する：

| 修飾キー | キー | Level 1 | Level 2 | Level 3 | ... |
| ---------- | ---- | ------- | ------- | ------- | --- |
| Cmd | N | ファイル | 新規 | | |
| Cmd+Shift | N | ファイル | 新規ウィンドウ | | |
| | | 表示 | ツールバーを表示 | | |
| Cmd+Opt | S | ファイル | 別名で保存... | | |

- 修飾キー: `Cmd`, `Shift`, `Opt`, `Ctrl` の組み合わせ（`+`区切り）。なければ空
- キー: ショートカットのキー文字。なければ空
- Level 1〜N: メニュー階層。トップメニュー→サブメニュー→...の順

### スプレッドシートの管理

- **命名規則**: `アプリ名_YYYY-MM-DD_HH-MM-SS`（例: `Safari_2026-01-31_20-45-30`）
- 実行するたびに新しいスプレッドシートを作成
- サービスアカウントのメールアドレスに共有される

## AppleScriptによるメニュー取得

System Events の `menu bar` → `menu bar item` → `menu` → `menu item` を再帰的に走査：

```applescript
tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
    tell process frontApp
        set menuBar to menu bar 1
        -- menu bar items を再帰的に走査
        -- 各 menu item の name と AX属性からショートカットキーを取得
    end tell
end tell
```

取得する Accessibility 属性：

- `name of menu item`: メニュー項目名
- `value of attribute "AXMenuItemCmdChar"`: ショートカットのキー文字（例: `"N"`, `"S"`）
- `value of attribute "AXMenuItemCmdModifiers"`: 修飾キーのビットマスク。デフォルト（0）= Cmd のみ
  - bit 0 (1): Shift
  - bit 1 (2): Option
  - bit 2 (4): Control
  - bit 3 (8): kMenuNoCommandModifier（Cmd キーなし）
  - 例: 0=Cmd, 1=Cmd+Shift, 3=Cmd+Shift+Opt, 8=修飾キーなし, 9=Shift のみ
- `value of attribute "AXMenuItemCmdGlyph"`: 特殊キーのグリフコード（矢印キー、Deleteなど）

## ライブラリのバンドル

Alfred Workflowでは外部ライブラリを `lib/` ディレクトリにバンドルする：

```bash
pip3 install --target=lib gspread google-auth   # または make deps
```

`lib/` は `.gitignore` 対象。`make build` 実行時に自動で `build/lib` にインストールされる。

`main.py` の先頭で `lib/` をパスに追加：

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
```

## Alfred ノード構成

```text
[Keyword "menu"] → [Run Script (Python)]
```

- **Keyword ノード**: キーワード `menu`、引数なし（`argumenttype=2`）
- **Run Script ノード**:

```xml
<key>script</key>
<string>/usr/bin/python3 main.py</string>
<key>scriptargtype</key>
<integer>0</integer>
<key>escaping</key>
<integer>0</integer>
<key>type</key>
<integer>0</integer>
```

完了通知はスクリプト内から `osascript -e 'display notification'` で発行する（Enter時点でAlfred UIは終了済み）。

## アイコン

- **ファイル**: `icon.png`
- **サイズ**: 512x512px
- **背景**: 周囲の余白は黒（`#000000`）で塗りつぶす

## Google サービスアカウント設定

### セットアップ手順

1. Google Cloud Console でプロジェクトを作成
2. Google Sheets API を有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. JSONキーを `credentials.json` としてワークフローディレクトリに配置

### セキュリティ注意事項

- `credentials.json` は絶対にGitにコミットしない（`.gitignore`に含める）
- サービスアカウントキーは最小権限の原則に従う
- スプレッドシートはサービスアカウントにのみ共有される（必要に応じて自分のGoogleアカウントにも共有）

## ディレクトリ構成

```text
alfred-menu-list/
├── CLAUDE.md
├── README.md
├── LICENSE                 ← MIT
├── main.py
├── menu_extractor.py
├── sheet_writer.py
├── info.plist
├── icon.png                ← 512x512px、余白は黒
├── Makefile
├── setup.cfg               ← flake8, mypy 設定
├── requirements.txt        ← gspread, google-auth（バージョン範囲指定）
├── requirements-dev.txt    ← pytest, flake8, mypy, black
├── .gitignore
├── credentials.json        ← サービスアカウントキー（gitignore対象）
├── lib/                    ← バンドルされた依存ライブラリ（gitignore対象）
├── venv/                   ← テスト用仮想環境（gitignore対象）
├── docs/
│   ├── PLAN.md
│   └── TODO.md
└── tests/
    ├── __init__.py
    ├── test_main.py
    ├── test_menu_extractor.py
    └── test_sheet_writer.py
```

## エラーハンドリング

すべてのエラーは macOS通知（`display notification`）でユーザーに表示する。

| エラー条件 | メッセージ例 | 処理 |
| ---------- | ----------- | ---- |
| アクセシビリティ権限なし | 「アクセシビリティ権限を許可してください」 | 通知後に終了 |
| `credentials.json` が存在しない | 「credentials.json が見つかりません」 | 通知後に終了 |
| ネットワーク接続なし / Google API エラー | 「スプレッドシートへの書き込みに失敗しました」 | 通知後に終了 |
| メニューバーなし（バックグラウンドプロセス等） | 「メニューバーが見つかりません」 | 通知後に終了 |
| メニュー項目が空 | 「メニュー項目が見つかりません: (アプリ名)」 | 通知後に終了 |

## テスト時の注意

- ワークフローを更新したら、必ずAlfred Preferencesで**既存のワークフローを削除**してから再インストール
- Alfredがキャッシュを使用する場合があるため、変更が反映されない場合はAlfredを再起動
- アクセシビリティ権限が必要：システム設定 > プライバシーとセキュリティ > アクセシビリティ でAlfredを許可
