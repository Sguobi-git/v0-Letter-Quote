import streamlit as st
import os
import json
from typing import Dict, List, Optional, Tuple, Any
import streamlit.components.v1 as components
import urllib.parse

def load_3d_viewer_html() -> str:
    """Load the 3D viewer HTML content."""
    try:
        with open(r"project/app/static/html/3d_viewer.html", 'r') as f:
            return f.read()
    except FileNotFoundError:
        st.error("3D viewer HTML file not found")
        return "<div>Error loading 3D preview</div>"

def load_available_fonts() -> List[str]:
    """Load available fonts for 3D letters."""
    try:
        if os.path.exists("data/fonts"):
            return [f.split('.')[0] for f in os.listdir("data/fonts") if f.endswith('.json')]
    except Exception as e:
        st.error(f"Error loading fonts: {e}")
    
    return ["default"]  # Return default font if no fonts found

def render_3d_preview() -> None:
    """Render the 3D letter preview component."""

    st.subheader("3D Letter Preview")
    # Insert the preview instructions message just above the 3D preview
    st.info("💡 To see your changes in the 3D preview, first click below on: ⏩ 'Next: Choose Options' ⏩ 'Calculate Quote' ⏩ 'Update 3D Preview'")
    
    # Get current letter properties from session state
    letter_props = st.session_state.letter_properties

    # Get the selected font from letter properties, fallback to 'helvetiker_bold' or 'default'
    font = letter_props.get('font', 'helvetiker_bold')

    # Create URL parameters with the current letter properties, including font
    params = {
        'letters': letter_props.get('letters', 'ABC'),
        'height': letter_props.get('height', 12.0),
        'width': letter_props.get('width', 8.0),
        'depth': letter_props.get('depth', 2.0),
        'material': letter_props.get('material', 'Wood'),
        'finish': letter_props.get('finish', 'Standard'),
        'color': letter_props.get('color_hex', '#2b5876'),
        'multiColor': 'false',
        'font': font
    }
    
    # Add LED lighting if enabled
    if letter_props.get('led_lighting', False):
        params['ledLighting'] = 'true'
    
    # Construct URL query string (not used directly, but could be for iframe src)
    query_string = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    
    # Add a loading spinner while the 3D viewer initializes
    with st.spinner("Loading 3D preview..."):
        # Embed the Three.js viewer with custom parameters
        viewer_html = load_3d_viewer_html()
        components.html(
            viewer_html + f"""
            <script>
                // Update viewer config with user parameters, including font
                document.addEventListener('DOMContentLoaded', () => {{
                    if (typeof viewer !== 'undefined' && viewer) {{
                        viewer.updateConfig({{
                            letters: '{params["letters"]}',
                            height: {params["height"]},
                            width: {params["width"]},
                            depth: {params["depth"]},
                            material: '{params["material"]}',
                            finish: '{params["finish"]}',
                            color: '{params["color"]}',
                            font: '{params["font"]}'  // Pass the font to the viewer
                            {", ledLighting: true" if params.get("ledLighting") == "true" else ""}
                        }});
                    }}
                }});
            </script>
            """, 
            height=450
        )
    
    # Interactive controls for the 3D view
    st.caption("Interactive Controls:")
    cols = st.columns(3)
    with cols[0]:
        st.button("Rotate View", key="rotate_view", on_click=lambda: st.markdown(
            """<script>
            if (window.toggleRotation) { window.toggleRotation(); }
            </script>""", 
            unsafe_allow_html=True
        ))
    with cols[1]:
        st.button("Reset View", key="reset_view", on_click=lambda: st.markdown(
            """<script>
            if (window.resetCamera) { window.resetCamera(); }
            </script>""", 
            unsafe_allow_html=True
        ))
    with cols[2]:
        st.button("Zoom to Fit", key="zoom_fit", on_click=lambda: st.markdown(
            """<script>
            if (window.zoomToFit) { window.zoomToFit(); }
            </script>""", 
            unsafe_allow_html=True
        ))

def update_3d_preview(letters: str, width: float, height: float, depth: float, 
                      font: str, color_map: Optional[Dict[str, str]] = None) -> None:
    """
    Update the 3D preview with new parameters.
    
    Args:
        letters: The letters to display
        width: Letter width in inches
        height: Letter height in inches
        depth: Letter depth in inches
        font: Font name to use
        color_map: Optional dictionary mapping each letter to its color
    """
    # Create config object with all parameters, including font
    config = {
        'letters': letters,
        'width': width,
        'height': height,
        'depth': depth,
        'font': font,  # Ensure font is properly included in the config
        'material': st.session_state.letter_properties.get('material', 'Wood'),
        'finish': st.session_state.letter_properties.get('finish', 'Standard'),
        'multiColor': color_map is not None
    }
    
    # Add LED lighting if enabled
    if st.session_state.letter_properties.get('led_lighting', False):
        config['ledLighting'] = True
    
    # Add color information
    if color_map is None:
        # Single color mode
        config['color'] = st.session_state.letter_properties.get('color_hex', '#2b5876')
    else:
        # Multi-color mode
        config['letterColors'] = color_map
    
    # Convert config to JSON
    config_json = json.dumps(config)
    
    # Update the 3D model by sending a message to the iframe, including font
    st.markdown(
        f"""
        <script>
            (function() {{
                // Find the iframe containing the 3D viewer
                const frames = document.getElementsByTagName('iframe');
                for (let i = 0; i < frames.length; i++) {{
                    try {{
                        console.log('Updating 3D preview with config:', {config_json});
                        // Send update message to the iframe
                        frames[i].contentWindow.postMessage({{
                            type: 'update_config',
                            config: {config_json}
                        }}, '*');
                    }} catch (e) {{
                        console.error('Error updating 3D preview:', e);
                    }}
                }}
            }})();
        </script>
        """,
        unsafe_allow_html=True
    )

    # For debugging - print the font being sent to the console
    st.markdown(
        f"""
        <script>
            console.log('Font being sent to 3D preview: {font}');
        </script>
        """,
        unsafe_allow_html=True
    )

def handle_font_upload() -> None:
    """Handle user font upload."""
    uploaded_font = st.file_uploader("Upload Custom Font (JSON)", type=["json"])
    
    if uploaded_font is not None:
        # Save the uploaded font
        try:
            font_data = json.load(uploaded_font)
            font_name = uploaded_font.name.split('.')[0]
            
            # Ensure the data directory exists
            os.makedirs("data/fonts", exist_ok=True)
            
            # Save the font data
            with open(f"data/fonts/{font_name}.json", "w") as f:
                json.dump(font_data, f)
            
            st.success(f"Font '{font_name}' uploaded successfully!")
            
            # Update the available fonts list
            st.session_state.available_fonts = load_available_fonts()
            st.session_state.letter_properties["font"] = font_name
            
            # Update the preview with the new font
            update_3d_preview(
                st.session_state.letter_properties["letters"],
                st.session_state.letter_properties["width"],
                st.session_state.letter_properties["height"],
                st.session_state.letter_properties["depth"],
                font_name
            )
            
        except Exception as e:
            st.error(f"Error uploading font: {e}")
