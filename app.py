import io
import json
import zipfile
from pathlib import Path

import streamlit as st

from neon_builder import build_sign_package

st.set_page_config(page_title="Neon Sign Builder", layout="wide")

st.title("Neon Sign Builder")
st.caption("Design a simple acrylic-backed faux-neon sign and export SVG files for xTool Creative Space.")

with st.sidebar:
    st.header("Design Options")
    sign_text = st.text_input("Sign text", value="Hello")
    width_in = st.slider("Overall width (inches)", min_value=6.0, max_value=36.0, value=18.0, step=0.5)
    height_in = st.slider("Overall height (inches)", min_value=4.0, max_value=24.0, value=10.0, step=0.5)

    font_style = st.selectbox(
        "Font style",
        ["Script", "Block", "Rounded", "Modern"],
        index=0,
    )

    led_color = st.selectbox(
        "LED color",
        ["Warm White", "Cool White", "Red", "Blue", "Green", "Pink", "Purple", "Orange"],
        index=0,
    )

    backing_shape = st.selectbox(
        "Backing shape",
        ["Rounded Rectangle", "Rectangle", "Capsule", "Arch"],
        index=0,
    )

    mount_style = st.selectbox(
        "Mount style",
        ["Wall Mount", "Shelf Stand", "None"],
        index=0,
    )

    include_star = st.checkbox("Add star accent", value=False)
    include_heart = st.checkbox("Add heart accent", value=False)

    backing_material = st.selectbox(
        "Backing material",
        ["Clear Cast Acrylic 3mm", "Black Cast Acrylic 3mm", "White Cast Acrylic 3mm"],
        index=0,
    )

    generate = st.button("Generate Project", type="primary")

st.markdown(
    """
This tool generates:
- Acrylic backing SVG
- LED placement template SVG
- Preview SVG
- Project manifest JSON
- A cutting and assembly plan text file
"""
)

if generate:
    decorative_elements = []
    if include_star:
        decorative_elements.append("star")
    if include_heart:
        decorative_elements.append("heart")

    package = build_sign_package(
        sign_text=sign_text,
        width_in=width_in,
        height_in=height_in,
        font_style=font_style,
        led_color=led_color,
        backing_shape=backing_shape,
        mount_style=mount_style,
        decorative_elements=decorative_elements,
        backing_material=backing_material,
    )

    st.subheader("Preview")
    st.image(package["preview_png_bytes"], caption="Rendered concept preview", use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Project Summary")
        st.write(f"**Text:** {sign_text}")
        st.write(f"**Size:** {width_in:.1f}\" W x {height_in:.1f}\" H")
        st.write(f"**Font Style:** {font_style}")
        st.write(f"**LED Color:** {led_color}")
        st.write(f"**Backing Shape:** {backing_shape}")
        st.write(f"**Mount Style:** {mount_style}")
        st.write(f"**Backing Material:** {backing_material}")

    with col2:
        st.subheader("xTool Import Notes")
        st.write("Import the backing SVG into xTool Creative Space as cut lines.")
        st.write("Import the LED template SVG as a reference guide layer.")
        st.write("Review material settings inside xTool before cutting.")
        st.code(package["cutting_plan_text"])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("backing.svg", package["backing_svg"])
        zf.writestr("led_template.svg", package["led_template_svg"])
        zf.writestr("preview.svg", package["preview_svg"])
        zf.writestr("project_manifest.json", json.dumps(package["manifest"], indent=2))
        zf.writestr("cutting_plan.txt", package["cutting_plan_text"])

    zip_buffer.seek(0)

    st.download_button(
        label="Download Project ZIP",
        data=zip_buffer.getvalue(),
        file_name="neon_sign_project.zip",
        mime="application/zip",
    )
