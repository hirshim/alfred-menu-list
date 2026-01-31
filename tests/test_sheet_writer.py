"""Tests for sheet_writer module."""

from unittest.mock import MagicMock, patch

import pytest

from sheet_writer import write_to_spreadsheet


class TestWriteToSpreadsheet:
    @patch("sheet_writer.gspread.authorize")
    @patch("sheet_writer.Credentials.from_service_account_file")
    def test_creates_spreadsheet_with_correct_title(
        self, mock_creds: MagicMock, mock_auth: MagicMock, tmp_path: MagicMock
    ) -> None:
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        mock_gc = MagicMock()
        mock_auth.return_value = mock_gc
        mock_sh = MagicMock()
        mock_sh.url = "https://docs.google.com/spreadsheets/d/xxx"
        mock_gc.create.return_value = mock_sh

        items = [("Cmd", "N", ["ファイル", "新規"])]
        url = write_to_spreadsheet("Safari", items, str(creds_file))

        assert url == "https://docs.google.com/spreadsheets/d/xxx"
        call_args = mock_gc.create.call_args[0][0]
        assert call_args.startswith("Safari_")

    @patch("sheet_writer.gspread.authorize")
    @patch("sheet_writer.Credentials.from_service_account_file")
    def test_writes_header_and_rows(
        self, mock_creds: MagicMock, mock_auth: MagicMock, tmp_path: MagicMock
    ) -> None:
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        mock_gc = MagicMock()
        mock_auth.return_value = mock_gc
        mock_sh = MagicMock()
        mock_sh.url = "https://example.com"
        mock_gc.create.return_value = mock_sh
        mock_ws = MagicMock()
        mock_sh.sheet1 = mock_ws

        items = [
            ("Cmd", "N", ["ファイル", "新規"]),
            ("Cmd+Shift", "N", ["ファイル", "新規ウィンドウ"]),
            ("", "", ["表示", "ツールバーを表示"]),
        ]
        write_to_spreadsheet("Safari", items, str(creds_file))

        call_args = mock_ws.update.call_args
        rows = call_args[0][0]

        assert rows[0] == ["修飾キー", "キー", "Level 1", "Level 2"]
        assert rows[1] == ["Cmd", "N", "ファイル", "新規"]
        assert rows[2] == ["Cmd+Shift", "N", "ファイル", "新規ウィンドウ"]
        assert rows[3] == ["", "", "表示", "ツールバーを表示"]

    @patch("sheet_writer.gspread.authorize")
    @patch("sheet_writer.Credentials.from_service_account_file")
    def test_pads_shorter_rows(
        self, mock_creds: MagicMock, mock_auth: MagicMock, tmp_path: MagicMock
    ) -> None:
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        mock_gc = MagicMock()
        mock_auth.return_value = mock_gc
        mock_sh = MagicMock()
        mock_sh.url = "https://example.com"
        mock_gc.create.return_value = mock_sh
        mock_ws = MagicMock()
        mock_sh.sheet1 = mock_ws

        items = [
            ("", "", ["ファイル", "書き出す", "PDF"]),
            ("Cmd", "N", ["ファイル", "新規"]),
        ]
        write_to_spreadsheet("App", items, str(creds_file))

        call_args = mock_ws.update.call_args
        rows = call_args[0][0]

        assert rows[0] == ["修飾キー", "キー", "Level 1", "Level 2", "Level 3"]
        assert rows[1] == ["", "", "ファイル", "書き出す", "PDF"]
        assert rows[2] == ["Cmd", "N", "ファイル", "新規", ""]

    def test_missing_credentials(self) -> None:
        with pytest.raises(FileNotFoundError, match="credentials.json"):
            write_to_spreadsheet("App", [], "/nonexistent/credentials.json")
