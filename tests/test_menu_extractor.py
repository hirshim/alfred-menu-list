"""Tests for menu_extractor module."""

from unittest.mock import MagicMock, patch

import pytest

from menu_extractor import (
    MenuBarNotFoundError,
    MenuExtractionError,
    _parse_output,
    decode_glyph,
    decode_modifiers,
    extract_menus,
    get_frontmost_app,
)


class TestDecodeModifiers:
    def test_cmd_only(self) -> None:
        assert decode_modifiers(0) == "Cmd"

    def test_cmd_shift(self) -> None:
        assert decode_modifiers(1) == "Cmd+Shift"

    def test_cmd_opt(self) -> None:
        assert decode_modifiers(2) == "Cmd+Opt"

    def test_cmd_shift_opt(self) -> None:
        assert decode_modifiers(3) == "Cmd+Shift+Opt"

    def test_cmd_ctrl(self) -> None:
        assert decode_modifiers(4) == "Cmd+Ctrl"

    def test_cmd_ctrl_shift(self) -> None:
        assert decode_modifiers(5) == "Cmd+Ctrl+Shift"

    def test_cmd_ctrl_opt(self) -> None:
        assert decode_modifiers(6) == "Cmd+Ctrl+Opt"

    def test_cmd_ctrl_shift_opt(self) -> None:
        assert decode_modifiers(7) == "Cmd+Ctrl+Shift+Opt"

    def test_no_cmd(self) -> None:
        # bit 3 (8) = kMenuNoCommandModifier
        assert decode_modifiers(8) == ""

    def test_shift_only_no_cmd(self) -> None:
        assert decode_modifiers(9) == "Shift"

    def test_opt_only_no_cmd(self) -> None:
        assert decode_modifiers(10) == "Opt"


class TestDecodeGlyph:
    def test_known_glyph(self) -> None:
        assert decode_glyph(111) == "F1"
        assert decode_glyph(122) == "F12"
        assert decode_glyph(100) == "←"
        assert decode_glyph(23) == "⌫"

    def test_unknown_glyph(self) -> None:
        assert decode_glyph(999) == "Glyph(999)"


class TestParseOutput:
    def test_basic_output(self) -> None:
        raw = "Safari\n0\tN\t\tファイル\t新規ウィンドウ\n"
        app_name, items = _parse_output(raw)
        assert app_name == "Safari"
        assert len(items) == 1
        modifier, key, levels = items[0]
        assert modifier == "Cmd"
        assert key == "N"
        assert levels == ["ファイル", "新規ウィンドウ"]

    def test_no_shortcut(self) -> None:
        raw = "Finder\n\t\t\t表示\tツールバーを表示\n"
        app_name, items = _parse_output(raw)
        assert app_name == "Finder"
        assert len(items) == 1
        modifier, key, levels = items[0]
        assert modifier == ""
        assert key == ""
        assert levels == ["表示", "ツールバーを表示"]

    def test_glyph_shortcut(self) -> None:
        raw = "TextEdit\n0\t\t111\t表示\tフルスクリーン\n"
        app_name, items = _parse_output(raw)
        modifier, key, levels = items[0]
        assert modifier == "Cmd"
        assert key == "F1"

    def test_cmd_shift(self) -> None:
        raw = "Safari\n1\tN\t\tファイル\t新規プライベートウィンドウ\n"
        _, items = _parse_output(raw)
        modifier, key, _ = items[0]
        assert modifier == "Cmd+Shift"
        assert key == "N"

    def test_multiple_items(self) -> None:
        raw = (
            "Finder\n"
            "0\tN\t\tファイル\t新規Finderウィンドウ\n"
            "0\tW\t\tファイル\tウィンドウを閉じる\n"
            "\t\t\t編集\tコピー\n"
        )
        app_name, items = _parse_output(raw)
        assert app_name == "Finder"
        assert len(items) == 3

    def test_deep_hierarchy(self) -> None:
        raw = "App\n\t\t\tファイル\t書き出す\tPDF\n"
        _, items = _parse_output(raw)
        assert items[0][2] == ["ファイル", "書き出す", "PDF"]

    def test_empty_output_raises(self) -> None:
        with pytest.raises(MenuExtractionError):
            _parse_output("")

    def test_app_name_only(self) -> None:
        app_name, items = _parse_output("Safari\n")
        assert app_name == "Safari"
        assert items == []


class TestGetFrontmostApp:
    @patch("menu_extractor.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Safari\n", stderr=""
        )
        assert get_frontmost_app() == "Safari"

    @patch("menu_extractor.subprocess.run")
    def test_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="error"
        )
        with pytest.raises(MenuExtractionError):
            get_frontmost_app()


class TestExtractMenus:
    @patch("menu_extractor.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Safari\n0\tN\t\tファイル\t新規\n",
            stderr="",
        )
        app_name, items = extract_menus()
        assert app_name == "Safari"
        assert len(items) == 1

    @patch("menu_extractor.subprocess.run")
    def test_menu_bar_not_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Can't get menu bar 1 of process",
        )
        with pytest.raises(MenuBarNotFoundError):
            extract_menus()

    @patch("menu_extractor.subprocess.run")
    def test_generic_error(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="some error"
        )
        with pytest.raises(MenuExtractionError):
            extract_menus()

    @patch("menu_extractor.subprocess.run")
    def test_timeout(self, mock_run: MagicMock) -> None:
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=60)
        with pytest.raises(MenuExtractionError, match="タイムアウト"):
            extract_menus()
