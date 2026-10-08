#!/usr/bin/env python3
"""Verify that bundled string catalogs have Simplified Chinese and Vietnamese translations."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOGS = [
    REPO_ROOT / "TypeWhisper/Resources/Localizable.xcstrings",
    REPO_ROOT / "TypeWhisper/Resources/InfoPlist.xcstrings",
    REPO_ROOT / "AppStore/Resources/InfoPlist.xcstrings",
    REPO_ROOT / "TypeWhisperWidgetExtension/Localizable.xcstrings",
    REPO_ROOT / "TypeWhisperTranscribeAction/InfoPlist.xcstrings",
    *sorted(
        (REPO_ROOT / "TypeWhisperPluginSDK/Plugins").glob(
            "*/Localizable.xcstrings"
        )
    ),
]
LANGUAGES = ("zh-Hans", "vi")


def localized_values(node: Any) -> list[str]:
    if not isinstance(node, dict):
        return []

    values: list[str] = []
    string_unit = node.get("stringUnit")
    if isinstance(string_unit, dict) and isinstance(string_unit.get("value"), str):
        values.append(string_unit["value"])

    for value in node.values():
        if isinstance(value, (dict, list)):
            values.extend(localized_values(value))
    return values


def main() -> int:
    missing: list[tuple[str, Path, str]] = []
    string_count = 0

    for catalog_path in CATALOGS:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        for key, entry in catalog.get("strings", {}).items():
            if key == "":
                continue
            string_count += 1
            localizations = entry.get("localizations", {})
            for language in LANGUAGES:
                values = localized_values(localizations.get(language))
                if not values or any(not value for value in values):
                    missing.append((language, catalog_path, key))

    if missing:
        print(f"error: {len(missing)} strings are missing complete localizations")
        for language, catalog_path, key in missing:
            print(f"  [{language}] {catalog_path.relative_to(REPO_ROOT)}: {key}")
        return 1

    print(
        f"verified {', '.join(LANGUAGES)} localizations for {string_count} strings "
        f"across {len(CATALOGS)} bundled catalogs"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
