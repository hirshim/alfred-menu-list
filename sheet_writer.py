"""Google Spreadsheet writer using gspread."""

import os
from datetime import datetime
from typing import List, Tuple

import gspread
from google.oauth2.service_account import Credentials

MenuItem = Tuple[str, str, List[str]]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def write_to_spreadsheet(
    app_name: str,
    items: List[MenuItem],
    credentials_path: str,
) -> str:
    """Write menu items to a new Google Spreadsheet.

    Args:
        app_name: Name of the application.
        items: List of (modifier, key, [levels]).
        credentials_path: Path to service account JSON key.

    Returns:
        URL of the created spreadsheet.
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"credentials.json が見つかりません: {credentials_path}"
        )

    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    gc = gspread.authorize(creds)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    title = f"{app_name}_{now}"
    sh = gc.create(title)

    max_depth = max((len(item[2]) for item in items), default=1)

    header = ["修飾キー", "キー"]
    for i in range(1, max_depth + 1):
        header.append(f"Level {i}")

    rows = [header]
    for modifier, key, levels in items:
        row = [modifier, key] + levels
        row.extend([""] * (len(header) - len(row)))
        rows.append(row)

    ws = sh.sheet1
    ws.update(rows, "A1")

    return sh.url
