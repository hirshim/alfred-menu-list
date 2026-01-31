"""Menu extractor using AppleScript (System Events)."""

import subprocess
from typing import Dict, List, Tuple

# Type alias: (modifier_string, key_string, [level1, level2, ...])
MenuItem = Tuple[str, str, List[str]]

# AXMenuItemCmdGlyph code to key name (Carbon Menus.h)
GLYPH_MAP: Dict[int, str] = {
    2: "Tab",
    4: "Enter",
    9: "Space",
    10: "⌦",
    11: "Return",
    23: "⌫",
    27: "Escape",
    28: "Clear",
    98: "Page Up",
    100: "←",
    101: "→",
    104: "↑",
    106: "↓",
    107: "Page Down",
    111: "F1",
    112: "F2",
    113: "F3",
    114: "F4",
    115: "F5",
    116: "F6",
    117: "F7",
    118: "F8",
    119: "F9",
    120: "F10",
    121: "F11",
    122: "F12",
    135: "F13",
    136: "F14",
    137: "F15",
    140: "Eject",
}


class MenuExtractionError(Exception):
    """Raised when menu extraction fails."""

    pass


class MenuBarNotFoundError(MenuExtractionError):
    """Raised when the application has no menu bar."""

    pass


def decode_modifiers(mask: int) -> str:
    """Decode AXMenuItemCmdModifiers bitmask.

    bit 0 (1): Shift, bit 1 (2): Option, bit 2 (4): Control,
    bit 3 (8): No Command key. Default (0) = Cmd only.
    """
    parts: List[str] = []
    if not (mask & 8):
        parts.append("Cmd")
    if mask & 4:
        parts.append("Ctrl")
    if mask & 1:
        parts.append("Shift")
    if mask & 2:
        parts.append("Opt")
    return "+".join(parts)


def decode_glyph(code: int) -> str:
    """Convert AXMenuItemCmdGlyph code to key name."""
    return GLYPH_MAP.get(code, f"Glyph({code})")


def get_frontmost_app() -> str:
    """Get the name of the frontmost application."""
    result = subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to return name of first '
            "application process whose frontmost is true",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise MenuExtractionError(result.stderr.strip())
    return result.stdout.strip()


def extract_menus() -> Tuple[str, List[MenuItem]]:
    """Extract all menu items from the frontmost application.

    Returns:
        (app_name, items) where each item is (modifier, key, levels).
    """
    script = _build_applescript()
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise MenuExtractionError("AppleScript がタイムアウトしました")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "menu bar" in stderr.lower():
            raise MenuBarNotFoundError(stderr)
        raise MenuExtractionError(stderr)

    return _parse_output(result.stdout)


def _build_applescript() -> str:
    """Build the AppleScript for recursive menu traversal."""
    return """\
on run
    set LF to (ASCII character 10)
    set TB to (ASCII character 9)
    set outputText to ""

    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        tell process frontApp
            set mb to menu bar 1
            repeat with mbi in (menu bar items of mb)
                set mbiName to name of mbi
                set outputText to outputText & ¬
                    my processMenu(menu 1 of mbi, mbiName, TB, LF)
            end repeat
        end tell
    end tell

    return frontApp & LF & outputText
end run

on processMenu(theMenu, pathSoFar, TB, LF)
    set outputText to ""
    tell application "System Events"
        repeat with mi in (menu items of theMenu)
            set n to name of mi
            if n is not missing value then
                set m to ""
                set c to ""
                set g to ""
                try
                    set raw to value of attribute "AXMenuItemCmdModifiers" of mi
                    if raw is not missing value then set m to raw as text
                end try
                try
                    set raw to value of attribute "AXMenuItemCmdChar" of mi
                    if raw is not missing value then set c to raw
                end try
                try
                    set raw to value of attribute "AXMenuItemCmdGlyph" of mi
                    if raw is not missing value and raw is not 0 then ¬
                        set g to raw as text
                end try

                set thisPath to pathSoFar & TB & n
                set outputText to outputText & ¬
                    m & TB & c & TB & g & TB & thisPath & LF

                try
                    set sub to menu 1 of mi
                    set outputText to outputText & ¬
                        my processMenu(sub, thisPath, TB, LF)
                end try
            end if
        end repeat
    end tell
    return outputText
end processMenu"""


def _parse_output(raw: str) -> Tuple[str, List[MenuItem]]:
    """Parse tab-delimited output from AppleScript.

    Format: first line is app name, subsequent lines are:
    MOD\\tCHAR\\tGLYPH\\tLEVEL1\\tLEVEL2\\t...
    """
    lines = raw.strip().split("\n")
    if not lines or not lines[0].strip():
        raise MenuExtractionError("AppleScript の出力が空です")

    app_name = lines[0].strip()
    items: List[MenuItem] = []

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue

        mod_raw, char_raw, glyph_raw = parts[0], parts[1], parts[2]
        levels = parts[3:]

        has_shortcut = bool(char_raw) or bool(glyph_raw)

        modifier = ""
        key = ""
        if has_shortcut:
            if mod_raw:
                modifier = decode_modifiers(int(mod_raw))
            if char_raw:
                key = char_raw
            elif glyph_raw:
                key = decode_glyph(int(glyph_raw))

        items.append((modifier, key, levels))

    return app_name, items
