#!/usr/bin/env python3

import json
import re
import zipfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PALETTE_DIR = BASE_DIR / "palettes"
INDEX_FILE = BASE_DIR / "index.json"


NAME_PATTERN = re.compile(
    r"--\s*name:\s*(.+)",
    re.IGNORECASE,
)

VERSION_PATTERN = re.compile(
    r"--\s*version:\s*(.+)",
    re.IGNORECASE,
)


def get_palette_metadata(archive):

    palette_files = [
        name
        for name in archive.namelist()
        if Path(name).name == "palette.lua"
    ]

    if not palette_files:
        raise ValueError(
            "palette.lua not found"
        )

    content = archive.read(
        palette_files[0]
    ).decode(
        "utf-8",
        errors="replace",
    )

    name_match = NAME_PATTERN.search(
        content
    )

    version_match = VERSION_PATTERN.search(
        content
    )

    if not name_match:
        raise ValueError(
            "name not found in palette.lua"
        )

    if not version_match:
        raise ValueError(
            "version not found in palette.lua"
        )

    name = name_match.group(1).strip()
    version = version_match.group(1).strip()

    return name, version


def scan_palettes():

    palettes = []

    if not PALETTE_DIR.exists():
        return palettes

    for zip_path in sorted(
        PALETTE_DIR.glob("*.zip"),
        key=lambda path: path.name.lower(),
    ):

        print(
            f"Checking: {zip_path.name}"
        )

        try:

            with zipfile.ZipFile(
                zip_path,
                "r",
            ) as archive:

                name, version = (
                    get_palette_metadata(
                        archive
                    )
                )

            palettes.append(
                {
                    "name": name,
                    "version": version,
                    "file": zip_path.name,
                }
            )

            print(
                f"  OK: {name} v{version}"
            )

        except zipfile.BadZipFile:

            print(
                "  ERROR: invalid ZIP"
            )

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

    return palettes


def write_index(palettes):

    data = {
        "palettes": palettes
    }

    with open(
        INDEX_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")


def main():

    palettes = scan_palettes()

    write_index(
        palettes
    )

    print()
    print(
        f"Generated: {INDEX_FILE}"
    )

    print(
        f"Palettes: {len(palettes)}"
    )


if __name__ == "__main__":
    main()
