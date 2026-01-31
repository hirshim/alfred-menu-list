"""Alfred Workflow: Extract menu items and write to Google Spreadsheet."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from menu_extractor import (  # noqa: E402
    AccessibilityError,
    MenuBarNotFoundError,
    MenuExtractionError,
    extract_menus,
)
from sheet_writer import write_to_spreadsheet  # noqa: E402


def notify(message: str, title: str = "alfred-menu-list") -> None:
    """Show macOS notification."""
    msg = message.replace("\\", "\\\\").replace('"', '\\"')
    ttl = title.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{msg}" with title "{ttl}"',
        ],
        timeout=10,
    )


def main() -> None:
    workflow_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(workflow_dir, "credentials.json")

    if not os.path.exists(credentials_path):
        notify("credentials.json が見つかりません")
        return

    try:
        app_name, items = extract_menus()

        if not items:
            notify(f"メニュー項目が見つかりません: {app_name}")
            return

        write_to_spreadsheet(app_name, items, credentials_path)
        notify(f"{app_name} のメニューをスプレッドシートに書き込みました")

    except AccessibilityError:
        notify("アクセシビリティ権限を許可してください")
    except MenuBarNotFoundError:
        notify("メニューバーが見つかりません")
    except MenuExtractionError:
        notify("メニュー取得に失敗しました")
    except Exception:
        notify("スプレッドシートへの書き込みに失敗しました")


if __name__ == "__main__":
    main()
