import io
from typing import Dict, List

import svgwrite
from PIL import Image, ImageDraw, ImageFont


DPI = 96
MM_PER_INCH = 25.4


def inches_to_px(value: float) -> int:
    return int(value * DPI)


def inches_to_mm(value: float) -> float:
    return value * MM_PER_INCH


def get_font(size: int, font_style: str):
    font_candidates = {
        "Script": ["DejaVuSans.ttf"],
        "Block": ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"],
        "Rounded": ["DejaVuSans.ttf"],
        "Modern": ["DejaVuSans.ttf"],
    }
    for candidate in font_candidates.get(font_style, ["DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def fit_text(sign_text: str, target_w: int, target_h: int, font_style: str):
    test_img = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(test_img)

    best_font = get_font(40, font_style)
    best_bbox = draw.textbbox((0, 0), sign_text, font=best_font)

    for size in range(20, 400):
        font = get_font(size, font_style)
        bbox = draw.textbbox((0, 0), sign_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w > target_w * 0.82 or text_h > target_h * 0.50:
            break
        best_font = font
        best_bbox = bbox

    return best_font, best_bbox


def led_rgb(led_color: str):
    mapping = {
        "Warm White": (255, 244, 214),
        "Cool White": (230, 245, 255),
        "Red": (255, 80, 80),
        "Blue": (80, 160, 255),
        "Green": (100, 255, 140),
        "Pink": (255, 120, 210),
        "Purple": (180, 120, 255),
        "Orange": (255, 170, 80),
    }
    return mapping.get(led_color, (255, 244, 214))


def build_backing_shape(dwg, shape_name: str, x: float, y: float, w: float, h: float):
    if shape_name == "Rectangle":
        return dwg.rect(insert=(x, y), size=(w, h), rx=0, ry=0)
    if shape_name == "Rounded Rectangle":
        r = min(w, h) * 0.08
        return dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r)
    if shape_name == "Capsule":
        r = h / 2
        return dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r)
    if shape_name == "Arch":
        path = dwg.path(fill="none")
        path.push(f"M {x},{y+h}")
        path.push(f"L {x},{y+h*0.30}")
        path.push(f"Q {x+w/2},{y-h*0.35} {x+w},{y+h*0.30}")
        path.push(f"L {x+w},{y+h}")
        path.push("Z")
        return path
    r = min(w, h) * 0.08
    return dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r)


def build_sign_package(
    sign_text: str,
    width_in: float,
    height_in: float,
    font_style: str,
    led_color: str,
    backing_shape: str,
    mount_style: str,
    decorative_elements: List[str],
    backing_material: str,
) -> Dict:
    canvas_w = inches_to_px(width_in)
    canvas_h = inches_to_px(height_in)

    margin = int(canvas_w * 0.06)
    backing_x = margin
    backing_y = margin
    backing_w = canvas_w - margin * 2
    backing_h = canvas_h - margin * 2

    preview = Image.new("RGBA", (canvas_w, canvas_h), (20, 20, 24, 255))
    draw = ImageDraw.Draw(preview)

    # backing preview bitmap
    draw.rounded_rectangle(
        [backing_x, backing_y, backing_x + backing_w, backing_y + backing_h],
        radius=max(12, int(min(backing_w, backing_h) * 0.06)),
        fill=(220, 230, 240, 60),
        outline=(180, 190, 205, 180),
        width=3,
    )

    font, bbox = fit_text(sign_text, backing_w, backing_h, font_style)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    tx = (canvas_w - text_w) // 2
    ty = (canvas_h - text_h) // 2 - bbox[1]

    rgb = led_rgb(led_color)

    for blur_offset in range(10, 0, -2):
        glow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.text((tx, ty), sign_text, font=font, fill=(*rgb, 28 + blur_offset * 6))
        preview.alpha_composite(glow)

    draw = ImageDraw.Draw(preview)
    draw.text((tx, ty), sign_text, font=font, fill=(*rgb, 255))

    if "star" in decorative_elements:
        draw.text(
            (backing_x + 24, backing_y + 24),
            "★",
            font=get_font(50, "Block"),
            fill=(*rgb, 220),
        )
    if "heart" in decorative_elements:
        draw.text(
            (backing_x + backing_w - 70, backing_y + 20),
            "♥",
            font=get_font(48, "Block"),
            fill=(*rgb, 220),
        )

    hole_r = 8
    wire_hole_center = (backing_x + backing_w - 24, backing_y + backing_h - 24)
    draw.ellipse(
        [
            wire_hole_center[0] - hole_r,
            wire_hole_center[1] - hole_r,
            wire_hole_center[0] + hole_r,
            wire_hole_center[1] + hole_r,
        ],
        outline=(255, 120, 120, 220),
        width=2,
    )

    mount_holes = []
    if mount_style == "Wall Mount":
        mount_holes = [
            (backing_x + 28, backing_y + 28),
            (backing_x + backing_w - 28, backing_y + 28),
        ]
        for cx, cy in mount_holes:
            draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(120, 220, 255, 220), width=2)

    if mount_style == "Shelf Stand":
        slot_w = 28
        slot_h = 8
        slot_y = backing_y + backing_h - 12
        slot1_x = backing_x + backing_w * 0.28
        slot2_x = backing_x + backing_w * 0.62
        draw.rounded_rectangle(
            [slot1_x, slot_y, slot1_x + slot_w, slot_y + slot_h],
            radius=3,
            outline=(120, 255, 120, 220),
            width=2,
        )
        draw.rounded_rectangle(
            [slot2_x, slot_y, slot2_x + slot_w, slot_y + slot_h],
            radius=3,
            outline=(120, 255, 120, 220),
            width=2,
        )

    # backing SVG
    dwg_backing = svgwrite.Drawing(
        size=(f"{width_in}in", f"{height_in}in"),
        viewBox=f"0 0 {canvas_w} {canvas_h}",
    )
    base_shape = build_backing_shape(
        dwg_backing, backing_shape, backing_x, backing_y, backing_w, backing_h
    )
    base_shape.update({"fill": "none", "stroke": "red", "stroke_width": 2})
    dwg_backing.add(base_shape)

    dwg_backing.add(
        dwg_backing.circle(
            center=wire_hole_center,
            r=hole_r,
            fill="none",
            stroke="blue",
            stroke_width=2,
        )
    )

    for cx, cy in mount_holes:
        dwg_backing.add(
            dwg_backing.circle(
                center=(cx, cy),
                r=7,
                fill="none",
                stroke="blue",
                stroke_width=2,
            )
        )

    if mount_style == "Shelf Stand":
        slot_w = 28
        slot_h = 8
        slot_y = backing_y + backing_h - 12
        slot1_x = backing_x + backing_w * 0.28
        slot2_x = backing_x + backing_w * 0.62
        dwg_backing.add(
            dwg_backing.rect(
                insert=(slot1_x, slot_y),
                size=(slot_w, slot_h),
                rx=3,
                ry=3,
                fill="none",
                stroke="green",
                stroke_width=2,
            )
        )
        dwg_backing.add(
            dwg_backing.rect(
                insert=(slot2_x, slot_y),
                size=(slot_w, slot_h),
                rx=3,
                ry=3,
                fill="none",
                stroke="green",
                stroke_width=2,
            )
        )

    # LED template SVG
    dwg_led = svgwrite.Drawing(
        size=(f"{width_in}in", f"{height_in}in"),
        viewBox=f"0 0 {canvas_w} {canvas_h}",
    )
    dwg_led.add(
        dwg_led.text(
            sign_text,
            insert=(tx, ty + text_h),
            fill="none",
            stroke="orange",
            stroke_width=1.5,
            font_size=font.size,
            font_family="DejaVu Sans",
            font_weight="bold" if font_style == "Block" else "normal",
        )
    )

    if "star" in decorative_elements:
        dwg_led.add(
            dwg_led.text(
                "★",
                insert=(backing_x + 24, backing_y + 64),
                fill="none",
                stroke="orange",
                stroke_width=1,
                font_size=48,
            )
        )
    if "heart" in decorative_elements:
        dwg_led.add(
            dwg_led.text(
                "♥",
                insert=(backing_x + backing_w - 70, backing_y + 62),
                fill="none",
                stroke="orange",
                stroke_width=1,
                font_size=46,
            )
        )

    # preview SVG
    dwg_preview = svgwrite.Drawing(
        size=(f"{width_in}in", f"{height_in}in"),
        viewBox=f"0 0 {canvas_w} {canvas_h}",
    )
    dwg_preview.add(
        dwg_preview.rect(
            insert=(0, 0),
            size=(canvas_w, canvas_h),
            fill="rgb(20,20,24)",
        )
    )

    base_preview_shape = build_backing_shape(
        dwg_preview, backing_shape, backing_x, backing_y, backing_w, backing_h
    )
    base_preview_shape.update(
        {
            "fill": "rgb(220,230,240)",
            "fill_opacity": 0.18,
            "stroke": "rgb(180,190,205)",
            "stroke_opacity": 0.8,
            "stroke_width": 2,
        }
    )
    dwg_preview.add(base_preview_shape)

    dwg_preview.add(
        dwg_preview.text(
            sign_text,
            insert=(tx, ty + text_h),
            fill=f"rgb({rgb[0]},{rgb[1]},{rgb[2]})",
            font_size=font.size,
            font_family="DejaVu Sans",
            font_weight="bold" if font_style == "Block" else "normal",
        )
    )

    preview_bytes = io.BytesIO()
    preview.save(preview_bytes, format="PNG")
    preview_bytes.seek(0)

    cutting_plan_text = f"""Suggested workflow for xTool P2
1. Import backing.svg into xTool Creative Space.
2. Set red lines as cut operations.
3. Set blue circles as hole cuts.
4. Set green slots as cut operations if using shelf stand.
5. Import led_template.svg as a reference layer only.
6. Material selected: {backing_material}
7. Confirm xTool EasySet / Material Settings Library values before final run.
8. Wire feed hole placed at lower-right corner.
9. Scale exported exactly at {width_in:.1f} in x {height_in:.1f} in.
"""

    manifest = {
        "sign_text": sign_text,
        "width_in": width_in,
        "height_in": height_in,
        "font_style": font_style,
        "led_color": led_color,
        "backing_shape": backing_shape,
        "mount_style": mount_style,
        "decorative_elements": decorative_elements,
        "backing_material": backing_material,
        "wire_hole_center_px": {"x": wire_hole_center[0], "y": wire_hole_center[1]},
        "mount_holes_px": [{"x": x, "y": y} for x, y in mount_holes],
    }

    return {
        "backing_svg": dwg_backing.tostring(),
        "led_template_svg": dwg_led.tostring(),
        "preview_svg": dwg_preview.tostring(),
        "preview_png_bytes": preview_bytes.getvalue(),
        "cutting_plan_text": cutting_plan_text,
        "manifest": manifest,
    }
