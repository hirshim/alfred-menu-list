"""Tests for main module."""

from unittest.mock import MagicMock, patch

from menu_extractor import (
    AccessibilityError,
    MenuBarNotFoundError,
    MenuExtractionError,
)


class TestMain:
    @patch("main.notify")
    @patch("main.os.path.exists", return_value=False)
    def test_missing_credentials(
        self, mock_exists: MagicMock, mock_notify: MagicMock
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with("credentials.json が見つかりません")

    @patch("main.notify")
    @patch("main.write_to_spreadsheet", return_value="https://example.com")
    @patch(
        "main.extract_menus",
        return_value=("Safari", [("Cmd", "N", ["ファイル", "新規"])]),
    )
    @patch("main.get_frontmost_app", return_value="Safari")
    @patch("main.os.path.exists", return_value=True)
    def test_success(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_write: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with(
            "Safari のメニューをスプレッドシートに書き込みました"
        )

    @patch("main.notify")
    @patch(
        "main.extract_menus",
        side_effect=MenuBarNotFoundError("no menu bar"),
    )
    @patch("main.get_frontmost_app", return_value="SomeApp")
    @patch("main.os.path.exists", return_value=True)
    def test_menu_bar_not_found(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with(
            "メニューバーが見つかりません: SomeApp"
        )

    @patch("main.notify")
    @patch(
        "main.extract_menus",
        side_effect=MenuExtractionError("error"),
    )
    @patch("main.get_frontmost_app", return_value="App")
    @patch("main.os.path.exists", return_value=True)
    def test_extraction_error(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with("メニュー取得に失敗しました")

    @patch("main.notify")
    @patch("main.extract_menus", return_value=("App", []))
    @patch("main.get_frontmost_app", return_value="App")
    @patch("main.os.path.exists", return_value=True)
    def test_no_items(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with("メニュー項目が見つかりません: App")

    @patch("main.notify")
    @patch(
        "main.extract_menus",
        side_effect=AccessibilityError("not allowed assistive access"),
    )
    @patch("main.get_frontmost_app", return_value="App")
    @patch("main.os.path.exists", return_value=True)
    def test_accessibility_error(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with(
            "アクセシビリティ権限を許可してください"
        )

    @patch("main.notify")
    @patch(
        "main.write_to_spreadsheet",
        side_effect=Exception("API error"),
    )
    @patch(
        "main.extract_menus",
        return_value=("App", [("Cmd", "N", ["ファイル", "新規"])]),
    )
    @patch("main.get_frontmost_app", return_value="App")
    @patch("main.os.path.exists", return_value=True)
    def test_spreadsheet_write_error(
        self,
        mock_exists: MagicMock,
        mock_get_app: MagicMock,
        mock_extract: MagicMock,
        mock_write: MagicMock,
        mock_notify: MagicMock,
    ) -> None:
        from main import main

        main()
        mock_notify.assert_called_once_with(
            "スプレッドシートへの書き込みに失敗しました"
        )
