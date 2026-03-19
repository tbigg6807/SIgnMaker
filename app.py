import io
import json
import zipfile

import streamlit as st

from neon_builder import build_sign_package

st.set_page_config(page_title="Neon Sign Builder", layout="wide")

st.title("Neon Sign Builder")
st.caption("Design a simple acrylic-backed faux-neon sign and export SVG files for xTool Creative Space.")
st.info("Adjust the options on the left. The sign preview updates automatically.")

with st.sidebar:
    st.header("Design Options")

    sign_text = st.text_input("Sign text", value="Hello")

    width_in = st.slider(
        "Overall width (inches)",
        min_value=6.0,
        max_value=36.0,
        value=18.0,
        step=0.5,
    )

    height_in = st.slider(
        "Overall height (inches)",
        min_value=4.0,
        max_value=24.0,
        value=10.0,
        step=0.5,
    )

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

    export_project = st.button("Generate Download Package", type="primary")

decorative_elements = []
if include_star:
    decorative_elements.append("star")
if include_heart:
    decorative_elements.append("heart")

# Live preview: runs automatically whenever a widget changes
try:
    live_package = build_sign_package(
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

    preview_col, info_col = st.columns([1.4, 1])

    with preview_col:
        st.subheader("Live Preview")
        st.image(
            live_package["preview_png_bytes"],
            caption="Real-time preview of the current sign design",
            use_container_width=True,
        )

    with info_col:
        st.subheader("Current Design")
        st.write(f"**Text:** {sign_text}")
        st.write(f"**Size:** {width_in:.1f}\" W x {height_in:.1f}\" H")
        st.write(f"**Font Style:** {font_style}")
        st.write(f"**LED Color:** {led_color}")
        st.write(f"**Backing Shape:** {backing_shape}")
        st.write(f"**Mount Style:** {mount_style}")
        st.write(f"**Backing Material:** {backing_material}")
        st.write(f"**Decor:** {', '.join(decorative_elements) if decorative_elements else 'None'}")

    with st.expander("xTool Import Notes", expanded=False):
        st.code(live_package["cutting_plan_text"])

except Exception as e:
    st.error(f"Preview generation failed: {e}")
    st.stop()

# Only create the downloadable ZIP when the user clicks the button
if export_project:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("backing.svg", live_package["backing_svg"])
        zf.writestr("led_template.svg", live_package["led_template_svg"])
        zf.writestr("preview.svg", live_package["preview_svg"])
        zf.writestr("project_manifest.json", json.dumps(live_package["manifest"], indent=2))
        zf.writestr("cutting_plan.txt", live_package["cutting_plan_text"])

    zip_buffer.seek(0)

    st.success("Project package generated successfully.")

    st.download_button(
        label="Download Project ZIP",
        data=zip_buffer.getvalue(),
        file_name="neon_sign_project.zip",
        mime="application/zip",
    )
