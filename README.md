# alfred-menu-list

最前面アプリのメニュー項目（全階層）をAppleScriptで取得し、ショートカットキー情報とともにGoogleスプレッドシートに書き込むAlfred Workflow。

## 必要条件

- macOS
- [Alfred](https://www.alfredapp.com/) + Powerpack
- アクセシビリティ権限（システム設定 > プライバシーとセキュリティ > アクセシビリティ でAlfredを許可）

## セットアップ

### 1. Google サービスアカウントの準備

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **Google Sheets API** を有効化
3. **サービスアカウント** を作成し、JSONキーをダウンロード
4. ダウンロードしたJSONキーを `credentials.json` にリネーム

### 2. インストール

1. [Releases](https://github.com/hirshim/alfred-menu-list/releases) から `.alfredworkflow` をダウンロード
2. ダウンロードしたファイルをダブルクリックしてAlfredにインストール
3. `credentials.json` をワークフローディレクトリに配置:
   - Alfred Preferences > Workflows > alfred-menu-list を右クリック > Open in Finder
   - `credentials.json` をそのフォルダにコピー

## 使い方

1. 記録したいアプリを最前面にする
2. Alfredを起動して `menu` と入力し、Enter
3. メニュー項目がGoogleスプレッドシートに書き込まれる（macOS通知で完了を通知）

スプレッドシートは `アプリ名_YYYY-MM-DD_HH-MM-SS` の名前で作成され、サービスアカウントに共有されます。自分のGoogleアカウントでアクセスするには、サービスアカウントのメールアドレスからスプレッドシートを共有してください。

## スプレッドシートの形式

| 修飾キー | キー | Level 1 | Level 2 | Level 3 |
| ---------- | ---- | ------- | ------- | ------- |
| Cmd | N | ファイル | 新規 | |
| Cmd+Shift | N | ファイル | 新規ウィンドウ | |
| | | 表示 | ツールバーを表示 | |

## 開発

```bash
# テスト環境セットアップ
python3 -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt

# コマンド
make test     # テスト実行
make lint     # flake8 + mypy
make format   # Blackでフォーマット
make build    # .alfredworkflowパッケージをビルド
make install  # ビルドしてAlfredにインストール
```

## ライセンス

MIT
