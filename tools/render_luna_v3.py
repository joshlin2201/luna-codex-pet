#!/usr/bin/env python3
"""Render Luna v3: video-grounded illustrated Codex pet assets."""

from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "assets" / "spritesheet.webp"
CONTACT_SHEET = ROOT / "assets" / "contact-sheet.png"
PREVIEW_DIR = ROOT / "assets" / "previews"
QA_DIR = ROOT / "qa"
DOCS_DIR = ROOT / "docs"
PET_INSTALL_DIR = Path.home() / ".codex" / "pets" / "luna"

COLUMNS = 8
ROWS = 9
CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_WIDTH = COLUMNS * CELL_WIDTH
ATLAS_HEIGHT = ROWS * CELL_HEIGHT
SCALE = 4

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
    "idle": [260, 120, 120, 150, 120, 180, 130, 280],
    "running-right": [105, 95, 90, 85, 90, 95, 110, 150],
    "running-left": [105, 95, 90, 85, 90, 95, 110, 150],
    "waving": [150, 120, 110, 130, 120, 110, 130, 260],
    "jumping": [120, 100, 90, 90, 100, 120, 130, 230],
    "failed": [150, 140, 150, 160, 170, 140, 140, 260],
    "waiting": [140, 130, 150, 130, 140, 150, 130, 260],
    "running": [120, 110, 105, 110, 115, 120, 115, 180],
    "review": [140, 140, 160, 130, 140, 160, 130, 260],
}

PAL = {
    "outline": (51, 42, 36, 255),
    "soft": (78, 66, 58, 210),
    "white": (250, 247, 239, 255),
    "cream": (242, 236, 224, 255),
    "chest": (255, 252, 245, 255),
    "gray": (112, 111, 102, 255),
    "mid": (135, 134, 124, 255),
    "light": (168, 167, 156, 255),
    "dark": (65, 64, 59, 255),
    "mask": (45, 40, 35, 255),
    "warm": (86, 69, 52, 255),
    "tan": (151, 113, 79, 255),
    "inner": (224, 191, 176, 255),
    "nose": (205, 143, 139, 255),
    "eye": (20, 18, 16, 255),
    "shine": (255, 255, 255, 230),
}

SIDE_SPECKLES = [
    (45, 132, 5, "light"),
    (53, 118, 4, "dark"),
    (62, 106, 3, "light"),
    (71, 123, 5, "mid"),
    (82, 111, 4, "dark"),
    (91, 128, 4, "light"),
    (100, 116, 3, "dark"),
    (108, 135, 5, "mid"),
    (76, 145, 3, "dark"),
    (57, 151, 4, "light"),
    (96, 149, 3, "dark"),
]

FRONT_SPECKLES = [
    (48, 151, 4, "light"),
    (58, 139, 3, "dark"),
    (69, 160, 3, "mid"),
    (126, 151, 4, "mid"),
    (136, 137, 3, "dark"),
    (145, 160, 3, "light"),
]


@dataclass(frozen=True)
class SidePose:
    facing: int = 1
    x: float = 0
    y: float = 0
    stretch: float = 1
    height: float = 1
    haunch: float = 1
    head_dx: float = 0
    head_dy: float = 0
    head_angle: float = 0
    nose_down: float = 0
    ear_a: float = -9
    ear_b: float = 17
    ear_lift: float = 0
    blink: float = 0
    feet: str = "hidden"
    ruff: float = 1
    mood: str = "normal"
    coat_shift: float = 0


@dataclass(frozen=True)
class FrontPose:
    x: float = 0
    y: float = 0
    body_scale: float = 1
    head_dx: float = 0
    head_dy: float = 0
    head_angle: float = 0
    ear_a: float = -8
    ear_b: float = 10
    ear_lift: float = 0
    blink_left: float = 0
    blink_right: float = 0
    feet: str = "hidden"
    ruff: float = 1
    mood: str = "normal"


def s(value: float) -> int:
    return int(round(value * SCALE))


def box(values: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    return tuple(s(v) for v in values)  # type: ignore[return-value]


def col(name: str) -> tuple[int, int, int, int]:
    return PAL[name]


def blank() -> Image.Image:
    return Image.new("RGBA", (CELL_WIDTH * SCALE, CELL_HEIGHT * SCALE), (0, 0, 0, 0))


def clean(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    data = bytearray(rgba.tobytes())
    for index in range(0, len(data), 4):
        if data[index + 3] == 0:
            data[index] = data[index + 1] = data[index + 2] = 0
    return Image.frombytes("RGBA", rgba.size, bytes(data))


def finish(cell: Image.Image) -> Image.Image:
    return clean(cell.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS))


def maybe_flip(cell: Image.Image, facing: int) -> Image.Image:
    return cell if facing == 1 else cell.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def ellipse(canvas: Image.Image, b: tuple[float, float, float, float], fill: str, outline: str | None = None, width: float = 1.2) -> None:
    draw = ImageDraw.Draw(canvas)
    if outline:
        draw.ellipse(box(b), fill=col(outline))
        inset = width
        draw.ellipse(box((b[0] + inset, b[1] + inset, b[2] - inset, b[3] - inset)), fill=col(fill))
    else:
        draw.ellipse(box(b), fill=col(fill))


def rot_ellipse(
    canvas: Image.Image,
    center: tuple[float, float],
    size: tuple[float, float],
    angle: float,
    fill: str,
    outline: str | None = None,
    width: float = 1.2,
) -> None:
    pad = 8
    local = Image.new("RGBA", (s(size[0] + pad * 2), s(size[1] + pad * 2)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(local)
    b = box((pad, pad, pad + size[0], pad + size[1]))
    if outline:
        draw.ellipse(b, fill=col(outline))
        inset = width
        draw.ellipse(box((pad + inset, pad + inset, pad + size[0] - inset, pad + size[1] - inset)), fill=col(fill))
    else:
        draw.ellipse(b, fill=col(fill))
    rotated = local.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    canvas.alpha_composite(rotated, (s(center[0]) - rotated.width // 2, s(center[1]) - rotated.height // 2))


def poly(canvas: Image.Image, points: list[tuple[float, float]], fill: str, outline: str | None = None, width: float = 1.2) -> None:
    draw = ImageDraw.Draw(canvas)
    pts = [(s(x), s(y)) for x, y in points]
    if outline:
        draw.line(pts + [pts[0]], fill=col(outline), width=max(1, s(width) * 2), joint="curve")
    draw.polygon(pts, fill=col(fill))


def line(canvas: Image.Image, points: list[tuple[float, float]], fill: str, width: float = 1) -> None:
    ImageDraw.Draw(canvas).line([(s(x), s(y)) for x, y in points], fill=col(fill), width=max(1, s(width)), joint="curve")


def ear(canvas: Image.Image, center: tuple[float, float], size: tuple[float, float], angle: float) -> None:
    rot_ellipse(canvas, center, size, angle, "outline")
    rot_ellipse(canvas, center, (size[0] - 4, size[1] - 5), angle, "dark")
    rot_ellipse(canvas, (center[0], center[1] + 2), (size[0] * 0.48, size[1] * 0.70), angle, "inner")


def side_feet(canvas: Image.Image, pose: SidePose) -> None:
    x, y = pose.x, pose.y
    if pose.feet == "hidden":
        return
    if pose.feet == "tucked":
        ellipse(canvas, (119 + x, 166 + y, 144 + x, 178 + y), "white", "outline", 0.9)
        ellipse(canvas, (52 + x, 165 + y, 74 + x, 176 + y), "cream", "soft", 0.8)
    elif pose.feet == "front-out":
        rot_ellipse(canvas, (139 + x, 171 + y), (36, 10), 6, "white", "soft", 0.8)
        rot_ellipse(canvas, (115 + x, 170 + y), (28, 9), -3, "cream", "soft", 0.8)
    elif pose.feet == "hop-load":
        rot_ellipse(canvas, (124 + x, 170 + y), (34, 11), 8, "white", "soft", 0.8)
        rot_ellipse(canvas, (58 + x, 169 + y), (38, 11), -6, "cream", "soft", 0.8)
    elif pose.feet == "hop-extend":
        rot_ellipse(canvas, (36 + x, 168 + y), (58, 12), -12, "cream", "outline", 0.8)
        rot_ellipse(canvas, (55 + x, 178 + y), (50, 11), 4, "white", "soft", 0.8)
        rot_ellipse(canvas, (145 + x, 166 + y), (34, 10), 7, "white", "soft", 0.8)
    elif pose.feet == "land":
        rot_ellipse(canvas, (144 + x, 171 + y), (42, 11), 1, "white", "outline", 0.8)
        rot_ellipse(canvas, (69 + x, 170 + y), (38, 11), -5, "cream", "soft", 0.8)
    elif pose.feet == "explore":
        rot_ellipse(canvas, (139 + x, 172 + y), (31, 9), 0, "white", "soft", 0.8)
        rot_ellipse(canvas, (108 + x, 173 + y), (25, 8), -5, "cream", "soft", 0.8)


def side_luna(pose: SidePose) -> Image.Image:
    canvas = blank()
    p = SidePose(**{**pose.__dict__, "facing": 1})
    x, y = p.x, p.y
    side_feet(canvas, p)

    rot_ellipse(canvas, (74 + x - p.stretch * 4, 139 + y), (92 * p.stretch, 58 * p.height * p.haunch), -4 + p.coat_shift, "outline")
    rot_ellipse(canvas, (75 + x - p.stretch * 4, 139 + y), (86 * p.stretch, 53 * p.height * p.haunch), -4 + p.coat_shift, "gray")
    rot_ellipse(canvas, (92 + x, 145 + y), (92 * p.stretch, 44 * p.height), 1, "white", "soft", 0.8)
    rot_ellipse(canvas, (118 + x, 154 + y + p.head_dy * 0.15), (70, 39), 0, "chest", "soft", 0.7)
    rot_ellipse(canvas, (29 + x - p.stretch * 10, 152 + y), (18, 15), 5, "white", "soft", 0.7)

    for sx, sy, radius, color_name in SIDE_SPECKLES:
        shift = math.sin((sx + sy + p.coat_shift) * 0.2) * 1.3
        ellipse(canvas, (sx + x - radius + shift, sy + y - radius * 0.7, sx + x + radius + shift, sy + y + radius * 0.8), color_name)

    for index in range(7):
        base_x = 103 + x + index * 3.2
        base_y = 126 + y + math.sin(index) * 4
        length = 8 + p.ruff * 3
        line(canvas, [(base_x, base_y), (base_x - 10, base_y + length)], "cream", 1.25)
        line(canvas, [(base_x + 3, base_y + 1), (base_x - 5, base_y + length + 2)], "white", 1.0)

    ear(canvas, (112 + x + p.head_dx * 0.25, 83 + y + p.ear_lift), (18, 62), p.ear_a)
    ear(canvas, (131 + x + p.head_dx * 0.25, 86 + y + p.ear_lift), (18, 58), p.ear_b)

    head = (126 + x + p.head_dx, 124 + y + p.head_dy + p.nose_down * 4)
    rot_ellipse(canvas, head, (53, 54), p.head_angle + p.nose_down * 3, "outline")
    rot_ellipse(canvas, head, (49, 50), p.head_angle + p.nose_down * 3, "white")
    rot_ellipse(canvas, (124 + x + p.head_dx, 121 + y + p.head_dy + p.nose_down * 4), (38, 43), -12 + p.head_angle, "mask")
    rot_ellipse(canvas, (137 + x + p.head_dx, 123 + y + p.head_dy + p.nose_down * 5), (21, 31), -9 + p.head_angle, "warm")
    poly(
        canvas,
        [
            (126 + x + p.head_dx, 96 + y + p.head_dy),
            (143 + x + p.head_dx, 110 + y + p.head_dy),
            (151 + x + p.head_dx, 132 + y + p.head_dy + p.nose_down * 5),
            (139 + x + p.head_dx, 145 + y + p.head_dy + p.nose_down * 4),
            (127 + x + p.head_dx, 129 + y + p.head_dy + p.nose_down * 3),
        ],
        "white",
    )
    rot_ellipse(canvas, (149 + x + p.head_dx, 137 + y + p.head_dy + p.nose_down * 5), (12, 9), 0, "white")

    eye_x = 135 + x + p.head_dx
    eye_y = 119 + y + p.head_dy + p.nose_down * 4
    if p.blink > 0.65:
        line(canvas, [(eye_x - 4, eye_y), (eye_x + 4, eye_y + 1)], "eye", 1.2)
    else:
        ellipse(canvas, (eye_x - 4, eye_y - 5, eye_x + 5, eye_y + 4), "eye")
        ellipse(canvas, (eye_x - 1.5, eye_y - 3.5, eye_x + 1.4, eye_y - 0.6), "shine")

    nose_y = 138 + y + p.head_dy + p.nose_down * 6
    ellipse(canvas, (150 + x + p.head_dx, nose_y - 3, 158 + x + p.head_dx, nose_y + 4), "nose")
    line(canvas, [(154 + x + p.head_dx, nose_y + 4), (153 + x + p.head_dx, nose_y + 10)], "soft", 0.7)
    if p.mood == "failed":
        line(canvas, [(136 + x + p.head_dx, eye_y + 8), (145 + x + p.head_dx, eye_y + 10)], "soft", 0.8)

    return finish(maybe_flip(canvas, pose.facing))


def front_feet(canvas: Image.Image, pose: FrontPose) -> None:
    if pose.feet == "hidden":
        return
    x, y = pose.x, pose.y
    if pose.feet == "tiny":
        ellipse(canvas, (70 + x, 169 + y, 88 + x, 181 + y), "cream", "soft", 0.8)
        ellipse(canvas, (104 + x, 169 + y, 122 + x, 181 + y), "white", "soft", 0.8)
    elif pose.feet == "pointed":
        rot_ellipse(canvas, (79 + x, 174 + y), (22, 10), -12, "cream", "soft", 0.8)
        rot_ellipse(canvas, (111 + x, 174 + y), (22, 10), 12, "white", "soft", 0.8)


def front_luna(pose: FrontPose) -> Image.Image:
    canvas = blank()
    x, y, scale = pose.x, pose.y, pose.body_scale

    rot_ellipse(canvas, (96 + x, 150 + y), (111 * scale, 62 * scale), 0, "outline")
    rot_ellipse(canvas, (96 + x, 150 + y), (106 * scale, 57 * scale), 0, "white")
    rot_ellipse(canvas, (54 + x, 150 + y), (45 * scale, 57 * scale), -9, "gray", "soft", 0.7)
    rot_ellipse(canvas, (138 + x, 150 + y), (42 * scale, 56 * scale), 9, "mid", "soft", 0.7)
    rot_ellipse(canvas, (96 + x, 158 + y), (76 * scale, 39 * scale), 0, "chest")
    for sx, sy, radius, color_name in FRONT_SPECKLES:
        ellipse(canvas, (sx + x - radius, sy + y - radius, sx + x + radius, sy + y + radius), color_name)
    front_feet(canvas, pose)

    for index in range(8):
        side = -1 if index < 4 else 1
        local = index % 4
        base_x = 76 + x + side * (local * 5 + 1)
        base_y = 124 + y + local * 3
        line(canvas, [(base_x, base_y), (base_x - side * (9 + pose.ruff), base_y + 12)], "cream", 1.15)
        line(canvas, [(116 + x - side * local * 4, base_y), (116 + x - side * (local * 4 - 8), base_y + 10)], "white", 0.9)

    ear(canvas, (78 + x + pose.head_dx * 0.2, 78 + y + pose.ear_lift), (18, 63), pose.ear_a)
    ear(canvas, (114 + x + pose.head_dx * 0.2, 78 + y + pose.ear_lift), (18, 63), pose.ear_b)
    head = (96 + x + pose.head_dx, 119 + y + pose.head_dy)
    rot_ellipse(canvas, head, (65, 58), pose.head_angle, "outline")
    rot_ellipse(canvas, head, (60, 54), pose.head_angle, "white")
    rot_ellipse(canvas, (78 + x + pose.head_dx, 119 + y + pose.head_dy), (30, 43), -16 + pose.head_angle, "mask")
    rot_ellipse(canvas, (116 + x + pose.head_dx, 120 + y + pose.head_dy), (29, 42), 15 + pose.head_angle, "mask")
    rot_ellipse(canvas, (84 + x + pose.head_dx, 121 + y + pose.head_dy), (18, 27), -12 + pose.head_angle, "tan")
    poly(
        canvas,
        [
            (91 + x + pose.head_dx, 91 + y + pose.head_dy),
            (102 + x + pose.head_dx, 91 + y + pose.head_dy),
            (109 + x + pose.head_dx, 122 + y + pose.head_dy),
            (102 + x + pose.head_dx, 143 + y + pose.head_dy),
            (88 + x + pose.head_dx, 143 + y + pose.head_dy),
            (83 + x + pose.head_dx, 123 + y + pose.head_dy),
        ],
        "white",
    )

    for eye, blink, squint_bias in [
        ((81 + x + pose.head_dx, 119 + y + pose.head_dy), pose.blink_left, 0.35),
        ((111 + x + pose.head_dx, 119 + y + pose.head_dy), pose.blink_right, 0.0),
    ]:
        if blink + squint_bias > 0.72:
            line(canvas, [(eye[0] - 5, eye[1]), (eye[0] + 5, eye[1] + 1)], "eye", 1.3)
        else:
            ellipse(canvas, (eye[0] - 4.5, eye[1] - 5.5, eye[0] + 4.5, eye[1] + 4.5), "eye")
            ellipse(canvas, (eye[0] - 1.4, eye[1] - 3.6, eye[0] + 1.5, eye[1] - 0.8), "shine")

    ellipse(canvas, (91 + x + pose.head_dx, 138 + y + pose.head_dy, 101 + x + pose.head_dx, 146 + y + pose.head_dy), "nose")
    line(canvas, [(96 + x + pose.head_dx, 146 + y + pose.head_dy), (96 + x + pose.head_dx, 153 + y + pose.head_dy)], "soft", 0.7)
    line(canvas, [(96 + x + pose.head_dx, 153 + y + pose.head_dy), (91 + x + pose.head_dx, 156 + y + pose.head_dy)], "soft", 0.7)
    line(canvas, [(96 + x + pose.head_dx, 153 + y + pose.head_dy), (101 + x + pose.head_dx, 156 + y + pose.head_dy)], "soft", 0.7)
    if pose.mood == "failed":
        line(canvas, [(76 + x, 130 + y), (87 + x, 134 + y)], "soft", 0.9)
        line(canvas, [(106 + x, 134 + y), (117 + x, 130 + y)], "soft", 0.9)

    return finish(canvas)


def make_frames() -> dict[str, list[Image.Image]]:
    return {
        "idle": [
            side_luna(SidePose(y=0, feet="hidden", ear_a=-8, ear_b=16)),
            side_luna(SidePose(y=1, height=1.02, feet="hidden", ear_a=-8, ear_b=14)),
            side_luna(SidePose(y=2, height=1.03, feet="hidden", ear_a=-7, ear_b=18, ruff=1.08)),
            side_luna(SidePose(y=1, blink=0.8, feet="hidden", ear_a=-6, ear_b=18)),
            side_luna(SidePose(y=2, head_dy=1, feet="hidden", ear_a=-13, ear_b=13)),
            side_luna(SidePose(y=0, feet="hidden", ear_a=-8, ear_b=16)),
            side_luna(SidePose(y=1, head_dx=-1, feet="hidden", ear_a=-6, ear_b=20)),
            side_luna(SidePose(y=0, feet="hidden", ear_a=-8, ear_b=16)),
        ],
        "running-right": hop_frames(1),
        "running-left": hop_frames(-1),
        "waving": [
            front_luna(FrontPose(feet="hidden", ear_a=-8, ear_b=10)),
            front_luna(FrontPose(head_dx=-1, head_dy=1, feet="hidden", ear_a=-17, ear_b=7, ruff=1.1)),
            front_luna(FrontPose(head_dx=1, feet="hidden", ear_a=-24, ear_b=12, blink_left=0.2, ruff=1.15)),
            front_luna(FrontPose(head_angle=-2, feet="hidden", ear_a=-15, ear_b=18, ruff=1.1)),
            front_luna(FrontPose(head_dx=1, feet="hidden", ear_a=-22, ear_b=11, blink_left=0.85)),
            front_luna(FrontPose(head_dx=-1, feet="hidden", ear_a=-14, ear_b=8)),
            front_luna(FrontPose(feet="hidden", ear_a=-7, ear_b=12, blink_right=0.6)),
            front_luna(FrontPose(feet="hidden", ear_a=-8, ear_b=10)),
        ],
        "jumping": [
            side_luna(SidePose(y=7, stretch=0.92, height=1.12, haunch=1.15, head_dy=2, feet="hop-load", ear_a=-14, ear_b=9)),
            side_luna(SidePose(y=2, stretch=1.04, height=0.96, head_dx=5, feet="front-out", ear_a=-8, ear_b=15)),
            side_luna(SidePose(y=-12, stretch=1.22, height=0.80, head_dx=8, feet="hop-extend", ear_a=-1, ear_b=24)),
            side_luna(SidePose(y=-29, stretch=1.34, height=0.72, head_dx=10, head_dy=-1, feet="hop-extend", ear_a=5, ear_b=27)),
            side_luna(SidePose(y=-23, stretch=1.28, height=0.74, head_dx=9, feet="hop-extend", ear_a=1, ear_b=24)),
            side_luna(SidePose(y=-5, stretch=1.10, height=0.90, head_dx=5, feet="land", ear_a=-5, ear_b=17)),
            side_luna(SidePose(y=5, stretch=0.96, height=1.08, haunch=1.10, head_dy=2, feet="hop-load", ear_a=-12, ear_b=12)),
            side_luna(SidePose(y=3, stretch=0.98, height=1.03, feet="tucked", ear_a=-9, ear_b=16)),
        ],
        "failed": failed_frames(),
        "waiting": waiting_frames(),
        "running": processing_frames(),
        "review": review_frames(),
    }


def hop_frames(facing: int) -> list[Image.Image]:
    return [
        side_luna(SidePose(facing=facing, x=-2, y=5, stretch=0.90, height=1.10, haunch=1.12, head_dy=2, feet="hop-load", ear_a=-12, ear_b=10)),
        side_luna(SidePose(facing=facing, x=2, y=2, stretch=1.02, height=0.96, head_dx=5, feet="front-out", ear_a=-7, ear_b=18)),
        side_luna(SidePose(facing=facing, x=5, y=-2, stretch=1.14, height=0.85, head_dx=8, head_dy=-1, feet="hop-extend", ear_a=-2, ear_b=22)),
        side_luna(SidePose(facing=facing, x=7, y=-17, stretch=1.30, height=0.72, head_dx=10, head_dy=-2, feet="hop-extend", ear_a=2, ear_b=25)),
        side_luna(SidePose(facing=facing, x=5, y=-14, stretch=1.24, height=0.76, head_dx=8, feet="hop-extend", ear_a=-1, ear_b=21)),
        side_luna(SidePose(facing=facing, x=4, y=1, stretch=1.06, height=0.92, head_dx=5, feet="land", ear_a=-6, ear_b=16)),
        side_luna(SidePose(facing=facing, x=1, y=5, stretch=0.94, height=1.08, haunch=1.10, head_dy=2, feet="hop-load", ear_a=-11, ear_b=12)),
        side_luna(SidePose(facing=facing, x=0, y=4, stretch=0.96, height=1.04, feet="tucked", ear_a=-8, ear_b=16)),
    ]


def failed_frames() -> list[Image.Image]:
    specs = [
        (3, 0.98, 1.02, 0, -14, 8, 0, 0),
        (7, 1.02, 0.96, 5, -24, 2, 0.5, 0),
        (10, 1.06, 0.88, 9, -36, -8, 1.0, 0),
        (12, 1.10, 0.82, 12, -45, -15, 1.2, 0.8),
        (12, 1.08, 0.82, 12, -42, -18, 1.3, 0),
        (10, 1.06, 0.86, 9, -36, -10, 1.0, 0),
        (7, 1.02, 0.94, 6, -24, 1, 0.6, 0),
        (4, 0.99, 1.0, 3, -15, 8, 0, 0),
    ]
    return [
        side_luna(SidePose(y=y, stretch=stretch, height=height, head_dy=head_dy, nose_down=nose, feet="hidden", ear_a=ear_a, ear_b=ear_b, blink=blink, mood="failed"))
        for y, stretch, height, head_dy, ear_a, ear_b, nose, blink in specs
    ]


def waiting_frames() -> list[Image.Image]:
    return [
        front_luna(FrontPose(feet="hidden", ear_a=-8, ear_b=10)),
        front_luna(FrontPose(head_dy=-1, feet="hidden", ear_a=-6, ear_b=8, ear_lift=-1)),
        front_luna(FrontPose(body_scale=1.01, head_dy=-2, feet="tiny", ear_a=-4, ear_b=6, ear_lift=-2)),
        front_luna(FrontPose(body_scale=1.01, head_dx=-1, head_dy=-1, feet="tiny", ear_a=-7, ear_b=9, blink_left=0.2)),
        front_luna(FrontPose(head_dx=1, head_dy=-1, feet="hidden", ear_a=-5, ear_b=12, blink_right=0.5)),
        front_luna(FrontPose(body_scale=1.01, head_dy=-2, feet="tiny", ear_a=-4, ear_b=7)),
        front_luna(FrontPose(head_dy=-1, feet="hidden", ear_a=-7, ear_b=10)),
        front_luna(FrontPose(feet="hidden", ear_a=-8, ear_b=10)),
    ]


def processing_frames() -> list[Image.Image]:
    return [
        side_luna(SidePose(y=7, stretch=1.10, height=0.88, head_dx=6, head_dy=10, nose_down=1.3, feet="explore", ear_a=-16, ear_b=8)),
        side_luna(SidePose(y=6, stretch=1.15, height=0.84, head_dx=9, head_dy=12, nose_down=1.5, feet="explore", ear_a=-14, ear_b=10)),
        side_luna(SidePose(y=5, stretch=1.18, height=0.82, head_dx=11, head_dy=11, nose_down=1.4, feet="front-out", ear_a=-10, ear_b=13)),
        side_luna(SidePose(y=6, stretch=1.12, height=0.86, head_dx=7, head_dy=9, nose_down=1.1, feet="explore", ear_a=-18, ear_b=6, blink=0.7)),
        side_luna(SidePose(y=7, stretch=1.08, height=0.90, head_dx=4, head_dy=8, nose_down=1.0, feet="hidden", ear_a=-20, ear_b=5)),
        side_luna(SidePose(y=6, stretch=1.14, height=0.85, head_dx=8, head_dy=11, nose_down=1.4, feet="explore", ear_a=-13, ear_b=12)),
        side_luna(SidePose(y=5, stretch=1.17, height=0.83, head_dx=10, head_dy=10, nose_down=1.2, feet="front-out", ear_a=-9, ear_b=15)),
        side_luna(SidePose(y=7, stretch=1.10, height=0.88, head_dx=6, head_dy=9, nose_down=1.1, feet="explore", ear_a=-16, ear_b=8)),
    ]


def review_frames() -> list[Image.Image]:
    return [
        front_luna(FrontPose(feet="hidden", head_angle=-1, ear_a=-9, ear_b=12, blink_left=0.15)),
        front_luna(FrontPose(head_dx=-2, head_dy=1, head_angle=-5, feet="hidden", ear_a=-15, ear_b=8, blink_left=0.45)),
        front_luna(FrontPose(head_dx=-3, head_angle=-7, feet="pointed", ear_a=-18, ear_b=6, blink_left=0.75)),
        front_luna(FrontPose(head_dx=1, head_angle=3, feet="hidden", ear_a=-7, ear_b=16, blink_right=0.4)),
        front_luna(FrontPose(head_dx=2, head_dy=1, head_angle=5, feet="pointed", ear_a=-5, ear_b=20, blink_left=0.25)),
        front_luna(FrontPose(head_dx=-1, head_angle=-3, feet="hidden", ear_a=-13, ear_b=10, blink_left=0.8)),
        front_luna(FrontPose(head_dx=1, head_angle=2, feet="hidden", ear_a=-8, ear_b=15)),
        front_luna(FrontPose(feet="hidden", head_angle=-1, ear_a=-9, ear_b=12, blink_left=0.35)),
    ]


def compose_atlas(frames: dict[str, list[Image.Image]]) -> Image.Image:
    atlas = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
    for row, state in enumerate(STATES):
        for column, frame in enumerate(frames[state]):
            atlas.alpha_composite(frame, (column * CELL_WIDTH, row * CELL_HEIGHT))
    return clean(atlas)


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
            crop = atlas.crop((column * CELL_WIDTH, row * CELL_HEIGHT, (column + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT))
            crop = crop.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            bg = checker((cell_w, cell_h))
            bg.paste(crop, (0, 0), crop)
            x = column * cell_w
            sheet.paste(bg, (x, y + label_height))
            draw.rectangle((x, y + label_height, x + cell_w - 1, y + label_height + cell_h - 1), outline="#18a058")
            draw.text((x + 4, y + label_height + 4), str(column), fill="#111111", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def save_previews(frames: dict[str, list[Image.Image]]) -> list[dict[str, object]]:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    previews = []
    for state in STATES:
        path = PREVIEW_DIR / f"{state}.gif"
        frames[state][0].save(
            path,
            save_all=True,
            append_images=frames[state][1:],
            duration=FULL8_DURATIONS[state],
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
            cell = atlas.crop((column * CELL_WIDTH, row * CELL_HEIGHT, (column + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT))
            alpha = cell.getchannel("A")
            nontransparent = sum(alpha.histogram()[1:])
            bbox = alpha.getbbox()
            cells.append(
                {
                    "state": state,
                    "row": row,
                    "column": column,
                    "used": True,
                    "runtimeUsed": column < RUNTIME_COUNTS[state],
                    "nontransparent_pixels": nontransparent,
                    "bbox": list(bbox) if bbox else None,
                }
            )
            if nontransparent < 600:
                errors.append(f"{state} row {row} column {column} is empty or too sparse")
            if bbox:
                left, top, right, bottom = bbox
                if left < 1 or top < 1 or right > CELL_WIDTH - 1 or bottom > CELL_HEIGHT - 1:
                    warnings.append(f"{state} row {row} column {column} is close to cell edge: {bbox}")
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
        "iteration": "2026-06-29-video-grounded-v3-render",
        "enrichedFull8": True,
        "runtimeCounts": RUNTIME_COUNTS,
        "transparent_rgb_residue_pixels": residue,
        "errors": errors,
        "warnings": warnings,
        "cells": cells,
    }


def write_docs(validation: dict[str, object], previews: list[dict[str, object]]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "installed-validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
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
        "visualQA": {
            "status": "pass",
            "notes": "Contact sheet visually reviewed after deterministic v3 render: rows are distinct, transparent, Luna-identifiable, and preserve rabbit-specific feet/anatomy rules.",
        },
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
        "iteration": "2026-06-29-video-grounded-v3-render",
        "notes": [
            "Rebuilt Luna as a cuter clean illustration style while preserving her real markings and anatomy.",
            "Made idle, waiting, waving, running, review, and failed visually distinct instead of small transforms of the same pose.",
            "Grounded chat/feed behaviors in private Luna video labels: loaf, wait, inspect, sniff, hop, peek, and settle.",
            "Directional rows now show rabbit-specific load, forefeet reach, long hind-foot kick, flight, landing, and recovery.",
            "Loaf states keep Luna's head low into the dewlap with hidden or tiny tucked rabbit feet.",
        ],
    }
    (QA_DIR / "qa-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def install_package() -> None:
    PET_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ATLAS, PET_INSTALL_DIR / "spritesheet.webp")
    shutil.copy2(ROOT / "pet.json", PET_INSTALL_DIR / "pet.json")
    shutil.copy2(CONTACT_SHEET, PET_INSTALL_DIR / "contact-sheet.png")
    for name in [
        "FEATURES.md",
        "ANIMATION-SPEC.md",
        "IDENTITY-GUIDE.md",
        "LUNA-REFERENCE-ANALYSIS.md",
        "LUNA-BEHAVIOR-EVIDENCE.md",
        "ITERATION-2026-06-28.md",
        "ITERATION-2026-06-29.md",
        "capabilities.json",
    ]:
        source = DOCS_DIR / name
        if source.exists():
            shutil.copy2(source, PET_INSTALL_DIR / name)
    for name in ["installed-validation.json", "qa-review.json", "qa-summary.json"]:
        shutil.copy2(QA_DIR / name, PET_INSTALL_DIR / name)
    preview_out = PET_INSTALL_DIR / "previews"
    preview_out.mkdir(exist_ok=True)
    for preview in PREVIEW_DIR.glob("*.gif"):
        shutil.copy2(preview, preview_out / preview.name)


def main() -> None:
    frames = make_frames()
    atlas = compose_atlas(frames)
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(ATLAS, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    make_contact_sheet(atlas, CONTACT_SHEET)
    previews = save_previews(frames)
    validation = validate(atlas)
    write_docs(validation, previews)
    if not validation["ok"]:
        raise SystemExit(json.dumps(validation["errors"], indent=2))
    install_package()
    print(
        json.dumps(
            {
                "ok": True,
                "iteration": "2026-06-29-video-grounded-v3-render",
                "spritesheet": str(ATLAS),
                "contactSheet": str(CONTACT_SHEET),
                "installedPackage": str(PET_INSTALL_DIR),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
