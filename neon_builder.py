from __future__ import annotations

import json

import streamlit as st

from neon_builder import (
    ACRYLIC_PRESETS,
    PREVIEW_COLORS,
    SignSpec,
    build_cutting_plan,
    export_zip,
    generate_project,
    render_backing_svg,
    render_led_template_svg,
    render_preview_svg,
)

st.set_page_config(page_title="Neon Sign Builder for xTool", layout="wide")

st.title("Neon Sign Builder for xTool P2")
st.caption("Design a simple faux-neon sign, preview it, and export SVG files ready to import into xTool Creative Space.")

with st.sidebar:
    st.header("Sign setup")
    text = st.text_input("Sign text", value="Hello")
    font_label = st.selectbox("Font style", ["Modern Sans", "Classic Serif", "Monoline", "Rounded"])
    led_color = st.selectbox("LED color", list(PREVIEW_COLORS.keys()), index=0)
    backing_color = st.color_picker("Backing preview color", value="#111111")

    st.header("Size and material")
    width_in = st.slider("Overall width (in)", 8.0, 36.0, 18.0, 0.5)
    height_in = st.slider("Overall height (in)", 4.0, 24.0, 10.0, 0.5)
    backing_material = st.selectbox("Backing material", list(ACRYLIC_PRESETS.keys()), index=1)
    margin_in = st.slider("Text margin from edge (in)", 0.25, 2.0, 0.8, 0.05)

    st.header("Construction")
    backing_style = st.selectbox("Backing shape", ["Rectangle", "Rounded Rectangle", "Capsule", "Arch"], index=1)
    mount_style = st.selectbox("Mounting", ["Wall Mount", "Shelf Stand", "Both", "None"], index=0)
    decor_style = st.selectbox("Decor", ["None", "Stars", "Hearts", "Sparkles"], index=0)
    hole_diameter_mm = st.slider("LED wire hole diameter (mm)", 4.0, 12.0, 6.0, 0.5)
    led_channel_offset_mm = st.slider("LED path display thickness (mm)", 1.0, 6.0, 2.2, 0.2)
    shelf_feet_depth_in = st.slider("Shelf foot depth (in)", 2.0, 6.0, 3.5, 0.25)

spec = SignSpec(
    text=text,
    font_label=font_label,
    led_color_name=led_color,
    backing_color=backing_color,
    backing_material=backing_material,
    width_in=width_in,
    height_in=height_in,
    backing_style=backing_style,
    mount_style=mount_style,
    decor_style=decor_style,
    margin_in=margin_in,
    hole_diameter_mm=hole_diameter_mm,
    led_channel_offset_mm=led_channel_offset_mm,
    shelf_feet_depth_in=shelf_feet_depth_in,
)

project = generate_project(spec)
preview_svg = render_preview_svg(project)
backing_svg = render_backing_svg(project)
led_svg = render_led_template_svg(project)
zip_bytes = export_zip(project)
plan_text = build_cutting_plan(project)

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Finished look preview")
    st.image(preview_svg)

    st.subheader("Manufacturing notes")
    st.text(plan_text)

with right:
    st.subheader("Outputs")
    st.download_button(
        "Download complete project ZIP",
        data=zip_bytes,
        file_name="neon_sign_project.zip",
        mime="application/zip",
        use_container_width=True,
    )
    st.download_button(
        "Download backing.svg",
        data=backing_svg,
        file_name="backing.svg",
        mime="image/svg+xml",
        use_container_width=True,
    )
    st.download_button(
        "Download led_template.svg",
        data=led_svg,
        file_name="led_template.svg",
        mime="image/svg+xml",
        use_container_width=True,
    )
    st.download_button(
        "Download preview.svg",
        data=preview_svg,
        file_name="preview.svg",
        mime="image/svg+xml",
        use_container_width=True,
    )

    with st.expander("Manifest / debug data"):
        st.json(project)

st.markdown("---")
st.subheader("How this export maps into xTool")
st.markdown(
    """
1. Import `backing.svg` into xTool Creative Space and assign cut operations to the outer profile and holes.
2. Import `led_template.svg` as a visual placement guide for your LED or faux-neon path.
3. In XCS, choose the matching acrylic profile from EasySet for the final cut job.
4. Use `preview.svg` only as a customer/mockup preview, not as a machining layer.

This app intentionally exports SVG because XCS supports importing SVG/DXF, while native XCS project files are created and saved by xTool software itself.
"""
)
