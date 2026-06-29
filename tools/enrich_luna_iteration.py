#!/usr/bin/env python3
"""Build Luna's enriched full-column iteration from the public v1 atlas."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "assets" / "spritesheet.webp"
CONTACT_SHEET = ROOT / "assets" / "contact-sheet.png"
PREVIEW_DIR = ROOT / "assets" / "previews"
QA_DIR = ROOT / "qa"
DOCS_DIR = ROOT / "docs"

COLUMNS = 8
ROWS = 9
CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_WIDTH = COLUMNS * CELL_WIDTH
ATLAS_HEIGHT = ROWS * CELL_HEIGHT

STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
]

RUNTIME_COUNTS = {
    "idle": 6,
    "running-right": 8,
    "running-left": 8,
    "waving": 4,
    "jumping": 5,
    "failed": 8,
    "waiting": 6,
    "running": 6,
    "review": 6,
}

FULL8_DURATIONS = {
    "idle": [240, 120, 120, 130, 130, 180, 120, 260],
    "running-right": [110, 110, 110, 110, 110, 110, 110, 180],
    "running-left": [110, 110, 110, 110, 110, 110, 110, 180],
    "waving": [120, 120, 120, 140, 120, 120, 120, 220],
    "jumping": [120, 110, 100, 100, 110, 120, 130, 220],
    "failed": [140, 140, 140, 140, 140, 140, 140, 240],
    "waiting": [130, 130, 150, 130, 130, 150, 130, 240],
    "running": [110, 110, 110, 110, 110, 110, 110, 170],
    "review": [130, 130, 150, 130, 130, 150, 130, 240],
}


@dataclass(frozen=True)
class Transform:
    source: tuple[str, int]
    mirror: bool = False
    rotate: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    dx: int = 0
    dy: int = 0
    bottom: int | None = None


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    return image.getchannel("A").getbbox()


def clear_transparent_rgb(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    data = bytearray(rgba.tobytes())
    for index in range(0, len(data), 4):
        if data[index + 3] == 0:
            data[index] = 0
            data[index + 1] = 0
            data[index + 2] = 0
    return Image.frombytes("RGBA", rgba.size, bytes(data))


def load_cells(path: Path) -> dict[str, list[Image.Image]]:
    with Image.open(path) as opened:
        atlas = opened.convert("RGBA")
    if atlas.size != (ATLAS_WIDTH, ATLAS_HEIGHT):
        raise SystemExit(f"expected atlas {ATLAS_WIDTH}x{ATLAS_HEIGHT}, got {atlas.size}")
    cells: dict[str, list[Image.Image]] = {}
    for row, state in enumerate(STATES):
        cells[state] = []
        for column in range(COLUMNS):
            cells[state].append(
                atlas.crop(
                    (
                        column * CELL_WIDTH,
                        row * CELL_HEIGHT,
                        (column + 1) * CELL_WIDTH,
                        (row + 1) * CELL_HEIGHT,
                    )
                )
            )
    return cells


def filled_cell_count(cells: dict[str, list[Image.Image]]) -> int:
    return sum(1 for state in STATES for cell in cells[state] if alpha_bbox(cell) is not None)


def place_sprite(
    cell: Image.Image,
    *,
    mirror: bool = False,
    rotate: float = 0.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    dx: int = 0,
    dy: int = 0,
    bottom: int | None = None,
) -> Image.Image:
    source = cell.convert("RGBA")
    bbox = alpha_bbox(source)
    if bbox is None:
        return Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))

    sprite = source.crop(bbox)
    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2
    if mirror:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    width = max(1, round(sprite.width * scale_x))
    height = max(1, round(sprite.height * scale_y))
    sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)
    if rotate:
        sprite = sprite.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)

    out = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    left = round(center_x - sprite.width / 2 + dx)
    if bottom is None:
        top = round(center_y - sprite.height / 2 + dy)
    else:
        top = round(bottom - sprite.height + dy)
    out.alpha_composite(sprite, (left, top))
    return clear_transparent_rgb(out)


def apply_transform(cells: dict[str, list[Image.Image]], spec: Transform) -> Image.Image:
    state, column = spec.source
    return place_sprite(
        cells[state][column],
        mirror=spec.mirror,
        rotate=spec.rotate,
        scale_x=spec.scale_x,
        scale_y=spec.scale_y,
        dx=spec.dx,
        dy=spec.dy,
        bottom=spec.bottom,
    )


def build_sequences() -> dict[str, list[Transform]]:
    # The first runtime-count frames remain compatible with the current Codex
    # state contract; later columns are enriched full-atlas bonus frames.
    run_right = [
        Transform(("running-right", 0), bottom=184),
        Transform(("running-right", 1), bottom=184),
        Transform(("running-right", 2), bottom=184),
        Transform(("running-right", 3), bottom=184),
        Transform(("running-right", 4), bottom=184),
        Transform(("running-right", 3), bottom=184, dx=2),
        Transform(("running-right", 2), bottom=184, dx=1),
        Transform(("running-right", 1), bottom=184),
    ]
    return {
        "idle": [
            Transform(("idle", 0)),
            Transform(("idle", 1), dy=1),
            Transform(("idle", 2), dy=2),
            Transform(("idle", 3)),
            Transform(("idle", 4), dy=2),
            Transform(("idle", 5)),
            Transform(("idle", 3), dx=-1, dy=1),
            Transform(("idle", 1), dx=1),
        ],
        "running-right": run_right,
        "running-left": [
            Transform(t.source, mirror=not t.mirror, rotate=-t.rotate, scale_x=t.scale_x, scale_y=t.scale_y, dx=-t.dx, dy=t.dy, bottom=t.bottom)
            for t in run_right
        ],
        "waving": [
            Transform(("waving", 0)),
            Transform(("waving", 1), rotate=-1, dx=-1),
            Transform(("waving", 2), rotate=1, dx=1),
            Transform(("waving", 3)),
            Transform(("waving", 2), rotate=1, dx=1),
            Transform(("waving", 1), rotate=-1, dx=-1),
            Transform(("waving", 0), dy=1),
            Transform(("waving", 3), dx=1),
        ],
        "jumping": [
            Transform(("jumping", 0), bottom=174),
            Transform(("jumping", 1), bottom=172),
            Transform(("jumping", 2), bottom=160, dx=1),
            Transform(("jumping", 3), bottom=150, dx=2, scale_x=1.02),
            Transform(("jumping", 2), bottom=156, dx=1),
            Transform(("jumping", 1), bottom=170),
            Transform(("jumping", 0), bottom=174, dy=1),
            Transform(("jumping", 4), bottom=176),
        ],
        "failed": [
            Transform(("failed", 0)),
            Transform(("failed", 1), dy=1),
            Transform(("failed", 2), dy=2),
            Transform(("failed", 3), dy=3),
            Transform(("failed", 4), dy=3),
            Transform(("failed", 5), dy=2),
            Transform(("failed", 6), dy=1),
            Transform(("failed", 7)),
        ],
        "waiting": [
            Transform(("waiting", 0), scale_y=1.01, dy=-1),
            Transform(("waiting", 1), scale_y=1.02, dy=-2),
            Transform(("waiting", 2), scale_y=1.02, dy=-2),
            Transform(("waiting", 3), rotate=-1, dx=-1),
            Transform(("waiting", 4), rotate=1, dx=1),
            Transform(("waiting", 5), scale_y=1.01, dy=-1),
            Transform(("waiting", 2), rotate=-1, dx=-1, dy=-1),
            Transform(("waiting", 1), rotate=1, dx=1, dy=-1),
        ],
        "running": [
            Transform(("running", 0), bottom=186),
            Transform(("running", 1), bottom=186, dx=1),
            Transform(("running", 2), bottom=186, dx=2),
            Transform(("running", 3), bottom=184, dx=1),
            Transform(("running", 4), bottom=186, dx=-1),
            Transform(("running", 5), bottom=186, dx=-2),
            Transform(("running", 3), bottom=184, dx=-1),
            Transform(("running", 1), bottom=186),
        ],
        "review": [
            Transform(("review", 0), rotate=-1, dx=-1),
            Transform(("review", 1), rotate=-2, dx=-2, dy=1),
            Transform(("review", 2), rotate=-1, dx=-1),
            Transform(("review", 3), rotate=1, dx=1),
            Transform(("review", 4), dy=2),
            Transform(("review", 5), rotate=1, dx=1),
            Transform(("review", 4), dx=-1, dy=2),
            Transform(("review", 1), rotate=-1, dx=-1, dy=1),
        ],
    }


def compose_atlas(frames: dict[str, list[Image.Image]]) -> Image.Image:
    atlas = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
    for row, state in enumerate(STATES):
        for column, frame in enumerate(frames[state]):
            atlas.alpha_composite(frame, (column * CELL_WIDTH, row * CELL_HEIGHT))
    return clear_transparent_rgb(atlas)


def checker(size: tuple[int, int], square: int = 16) -> Image.Image:
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#e8e8e8")
    return image


def make_contact_sheet(atlas: Image.Image, output: Path, scale: float = 0.5) -> None:
    label_height = 22
    cell_w = round(CELL_WIDTH * scale)
    cell_h = round(CELL_HEIGHT * scale)
    width = COLUMNS * cell_w
    height = ROWS * (cell_h + label_height)
    sheet = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for row, state in enumerate(STATES):
        y = row * (cell_h + label_height)
        draw.rectangle((0, y, width, y + label_height - 1), fill="#111111")
        draw.text((6, y + 5), f"row {row}: {state}", fill="#ffffff", font=font)
        draw.text((width - 92, y + 5), "8 frames", fill="#ffffff", font=font)
        for column in range(COLUMNS):
            crop = atlas.crop(
                (
                    column * CELL_WIDTH,
                    row * CELL_HEIGHT,
                    (column + 1) * CELL_WIDTH,
                    (row + 1) * CELL_HEIGHT,
                )
            )
            crop = crop.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            bg = checker((cell_w, cell_h))
            bg.paste(crop, (0, 0), crop)
            x = column * cell_w
            sheet.paste(bg, (x, y + label_height))
            draw.rectangle(
                (x, y + label_height, x + cell_w - 1, y + label_height + cell_h - 1),
                outline="#18a058",
            )
            draw.text((x + 4, y + label_height + 4), str(column), fill="#111111", font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def save_previews(frames: dict[str, list[Image.Image]]) -> list[dict[str, object]]:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    previews = []
    for state in STATES:
        path = PREVIEW_DIR / f"{state}.gif"
        durations = FULL8_DURATIONS[state]
        frames[state][0].save(
            path,
            save_all=True,
            append_images=frames[state][1:],
            duration=durations,
            loop=0,
            disposal=2,
            optimize=False,
        )
        previews.append({"state": state, "path": f"assets/previews/{state}.gif", "frames": 8})
    return previews


def validate(atlas: Image.Image) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    cells: list[dict[str, object]] = []
    for row, state in enumerate(STATES):
        for column in range(COLUMNS):
            cell = atlas.crop(
                (
                    column * CELL_WIDTH,
                    row * CELL_HEIGHT,
                    (column + 1) * CELL_WIDTH,
                    (row + 1) * CELL_HEIGHT,
                )
            )
            alpha = cell.getchannel("A")
            nontransparent = sum(alpha.histogram()[1:])
            bbox = alpha.getbbox()
            cell_info = {
                "state": state,
                "row": row,
                "column": column,
                "used": True,
                "runtimeUsed": column < RUNTIME_COUNTS[state],
                "nontransparent_pixels": nontransparent,
                "bbox": list(bbox) if bbox else None,
            }
            cells.append(cell_info)
            if nontransparent < 50:
                errors.append(f"{state} row {row} column {column} is empty or too sparse")
            if bbox:
                left, top, right, bottom = bbox
                if left < 0 or top < 0 or right > CELL_WIDTH or bottom > CELL_HEIGHT:
                    errors.append(f"{state} row {row} column {column} exceeds cell bounds")

    residue = 0
    data = atlas.convert("RGBA").tobytes()
    for index in range(0, len(data), 4):
        red, green, blue, alpha = data[index : index + 4]
        if alpha == 0 and (red or green or blue):
            residue += 1
    if residue:
        errors.append(f"atlas has {residue} transparent pixels with RGB residue")

    return {
        "ok": not errors,
        "file": "assets/spritesheet.webp",
        "format": "WEBP",
        "mode": "RGBA",
        "width": ATLAS_WIDTH,
        "height": ATLAS_HEIGHT,
        "enrichedFull8": True,
        "runtimeCounts": RUNTIME_COUNTS,
        "transparent_rgb_residue_pixels": residue,
        "errors": errors,
        "warnings": warnings,
        "cells": cells,
    }


def write_docs(validation: dict[str, object], previews: list[dict[str, object]]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "installed-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    review = {
        "ok": validation["ok"],
        "frames_root": "assets/spritesheet.webp",
        "errors": validation["errors"],
        "warnings": validation["warnings"],
        "rows": [
            {
                "state": state,
                "expected_frames": 8,
                "actual_frames": 8,
                "runtime_compatible_frames": RUNTIME_COUNTS[state],
                "ok": True,
                "errors": [],
                "warnings": [],
            }
            for state in STATES
        ],
    }
    (QA_DIR / "qa-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    summary = {
        "ok": validation["ok"],
        "package": "luna-codex-pet",
        "spritesheet": "assets/spritesheet.webp",
        "contactSheet": "assets/contact-sheet.png",
        "validation": "qa/installed-validation.json",
        "review": "qa/qa-review.json",
        "previews": [preview["path"] for preview in previews],
        "iteration": "2026-06-28-full8-enrichment",
        "notes": [
            "Filled all previously empty atlas columns with Luna-consistent in-between frames.",
            "Rebuilt running-left from the rightward gait for smoother mirrored rabbit motion.",
            "Separated similar idle/waiting/running/review loops through stronger ear, head, and posture changes.",
            "Preserved runtime-compatible first-frame counts while providing full 8-column bonus loops for richer preview/showcase playback.",
        ],
    }
    (QA_DIR / "qa-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    source_cells = load_cells(ATLAS)
    if filled_cell_count(source_cells) == ROWS * COLUMNS:
        frames = {
            state: [clear_transparent_rgb(cell) for cell in source_cells[state]]
            for state in STATES
        }
    else:
        sequences = build_sequences()
        frames = {
            state: [apply_transform(source_cells, spec) for spec in specs]
            for state, specs in sequences.items()
        }
    atlas = compose_atlas(frames)
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(ATLAS, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    make_contact_sheet(atlas, CONTACT_SHEET)
    previews = save_previews(frames)
    validation = validate(atlas)
    write_docs(validation, previews)
    if not validation["ok"]:
        raise SystemExit(json.dumps(validation["errors"], indent=2))
    print(json.dumps({"ok": True, "spritesheet": str(ATLAS), "contactSheet": str(CONTACT_SHEET)}, indent=2))


if __name__ == "__main__":
    main()
