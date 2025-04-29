import streamlit as st
import json
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd

from utils.calculations import calculate_costs, calculate_delivery_time, calculate_bulk_discount
from utils.validation import validate_inputs, sanitize_text_input
from utils.formatting import format_currency
from utils.export import export_to_csv, export_to_pdf
from components.letter_preview import update_3d_preview, load_available_fonts, handle_font_upload

def render_quotation_form() -> None:
    """Render the quotation form with a two-step process: first letters/font, then main options."""

    # Material options with their rates
    material_options = {
        "Wood": {"rate": 0.030},
        "Acrylic": {"rate": 0.0375},
        "Metal": {"rate": 0.045},
        "Foam": {"rate": 0.020}
    }

    # Color options with their hex values
    color_options = {
        "Blue": "#2b5876",
        "Red": "#b22222",
        "Green": "#228b22",
        "Black": "#000000",
        "White": "#ffffff",
        "Gold": "#ffd700",
        "Silver": "#c0c0c0",
        "Bronze": "#cd7f32",
        "Purple": "#800080",
        "Orange": "#ffa500"
    }

    # Check if we need to reuse a saved quotation
    duplicate_mode = st.session_state.get("duplicate_quotation_index") is not None

    if duplicate_mode:
        # Load the selected quotation data to duplicate
        index = st.session_state.duplicate_quotation_index
        if 0 <= index < len(st.session_state.quotations):
            quoted_data = st.session_state.quotations[index]
            # Pre-fill session state with the quoted data
            for key, value in quoted_data.items():
                if key in st.session_state.letter_properties:
                    st.session_state.letter_properties[key] = value

            # Clear the duplicate flag
            st.session_state.duplicate_quotation_index = None
            st.success("Quotation loaded. You can now modify it.")

    # --- STEP 1: Small form for letters and font selection ---
    st.header("Step 1: Enter Letters and Choose Font")
    with st.form("letters_font_form", clear_on_submit=False):
        # Letters input
        letters = st.text_input(
            "Enter Letters/Text",
            value=st.session_state.letter_properties.get("letters", "LOGO"),
            max_chars=20,
            help="Enter the letters you want to create (max 20 characters)",
            key="step1_letters"
        )
        letters = sanitize_text_input(letters)
        num_letters = len(letters.strip())

        # Font selection
        font_options = [
            ("helvetiker_bold", "Helvetiker Bold"),
            ("helvetiker_regular", "Helvetiker Regular"),
            ("optimer_bold", "Optimer Bold"),
            ("optimer_regular", "Optimer Regular"),
            ("gentilis_bold", "Gentilis Bold"),
            ("gentilis_regular", "Gentilis Regular"),
            ("droid_sans", "Droid Sans"),
            ("droid_serif", "Droid Serif"),
            ("roboto_regular", "Roboto Regular"),
            ("roboto_bold", "Roboto Bold"),
            ("times_new_roman", "Times New Roman"),
            ("arial", "Arial"),
            ("comic_sans", "Comic Sans"),
            ("georgia", "Georgia"),
            ("impact", "Impact"),
            ("verdana", "Verdana"),
            ("custom", "Custom Font (Upload below)")
        ]

        loaded_fonts = load_available_fonts()
        font_dict = {k: v for k, v in font_options}
        for f in loaded_fonts:
            if f not in font_dict:
                font_dict[f] = f.replace("_", " ").title()
        final_font_options = [(k, v) for k, v in font_dict.items()]

        current_font_key = st.session_state.letter_properties.get("font", "helvetiker_bold")
        font_keys = [k for k, v in final_font_options]
        font_display_names = [v for k, v in final_font_options]
        if current_font_key in font_keys:
            font_index = font_keys.index(current_font_key)
        else:
            font_index = 0

        font_display = st.selectbox(
            "Font Style",
            options=font_display_names,
            index=font_index,
            key="step1_font"
        )
        font = font_keys[font_display_names.index(font_display)]

        font_upload_expander = st.expander("Upload Custom Font")
        with font_upload_expander:
            handle_font_upload()

        # --- Live 3D preview for font selection step ---
        # Show a live preview of the letters with the selected font
        st.markdown("#### Live 3D Preview")
        # For the preview, use the current letters and font, and default size/colors
        preview_letters = letters
        preview_height = st.session_state.letter_properties.get("height", 12.0)
        preview_width = st.session_state.letter_properties.get("width", 8.0)
        preview_depth = st.session_state.letter_properties.get("depth", 2.0)
        preview_font = font
        # Use default color blue for all letters in this step
        preview_letter_color_map = {i: "#2b5876" for i in range(len(preview_letters.strip()))}
        update_3d_preview(
            preview_letters,
            preview_height,
            preview_width,
            preview_depth,
            preview_font,
            preview_letter_color_map
        )
        st.caption("Preview updates as you type or change font. (Font will be reflected in the 3D preview)")

        step1_submit = st.form_submit_button("Next: Choose Options", type="primary", use_container_width=True)

    if step1_submit:
        st.session_state.letter_properties["letters"] = letters
        st.session_state.letter_properties["font"] = font
        st.session_state["step1_completed"] = True
        if "current_quote" in st.session_state:
            del st.session_state.current_quote

    if st.session_state.get("step1_completed", False) and st.session_state.letter_properties.get("letters", "").strip():
        form_col, preview_col = st.columns([3, 2])

        with form_col:
            with st.form("quotation_form", clear_on_submit=False):
                st.subheader("Step 2: Choose Options for Your Letters")

                letters = st.session_state.letter_properties["letters"]
                font = st.session_state.letter_properties["font"]
                num_letters = len(letters.strip())

                material = st.selectbox(
                    "Material Type",
                    options=list(material_options.keys()),
                    index=list(material_options.keys()).index(st.session_state.letter_properties.get("material", "Acrylic"))
                        if st.session_state.letter_properties.get("material", "Acrylic") in material_options else 0,
                    key="input_material"
                )

                st.subheader("Dimensions (per letter)")
                col_h, col_w, col_d = st.columns(3)

                with col_h:
                    height = st.number_input(
                        "Height (inches)",
                        min_value=1.0,
                        max_value=120.0,
                        value=st.session_state.letter_properties.get("height", 12.0),
                        step=0.5,
                        key="input_height"
                    )

                with col_w:
                    width = st.number_input(
                        "Width (inches)",
                        min_value=1.0,
                        max_value=120.0,
                        value=st.session_state.letter_properties.get("width", 8.0),
                        step=0.5,
                        key="input_width"
                    )

                with col_d:
                    depth = st.number_input(
                        "Depth (inches)",
                        min_value=0.5,
                        max_value=24.0,
                        value=st.session_state.letter_properties.get("depth", 2.0),
                        step=0.5,
                        key="input_depth"
                    )

                st.subheader("Order Details")
                col_q, col_f = st.columns(2)

                with col_q:
                    quantity = st.number_input(
                        "Sets of Letters",
                        min_value=1,
                        value=st.session_state.letter_properties.get("quantity", 1),
                        step=1,
                        help=f"Each set contains {num_letters} letters",
                        key="input_quantity"
                    )

                with col_f:
                    finish_options = ["Standard", "Painted", "High Gloss", "Matte"]
                    finish = st.selectbox(
                        "Finish Type",
                        options=finish_options,
                        index=finish_options.index(st.session_state.letter_properties.get("finish", "Standard"))
                            if st.session_state.letter_properties.get("finish", "Standard") in finish_options else 0,
                        key="input_finish"
                    )

                total_letters = num_letters * quantity
                st.info(f"Total letters to be produced: {total_letters}")

                # --- Single color selection for the whole word ---
                st.subheader("Color Selection (choose a color for the word)")

                # Default color
                default_color = st.session_state.letter_properties.get("color", "Blue")
                selected_color = st.selectbox(
                    "Color",
                    options=list(color_options.keys()),
                    index=list(color_options.keys()).index(default_color)
                        if default_color in color_options else 0,
                    key="input_color_word"
                )

                # Store color info in session state
                st.session_state.letter_properties["color"] = selected_color
                st.session_state.letter_properties["color_hex"] = color_options[selected_color]
                st.session_state.letter_properties["multi_color"] = False
                # For compatibility, fill letter_colors with all letters having the same color
                letter_colors = {}
                for i, letter in enumerate(letters.strip()):
                    letter_colors[str(i)] = {
                        "name": selected_color,
                        "hex": color_options[selected_color],
                        "char": letter
                    }
                st.session_state.letter_properties["letter_colors"] = letter_colors

                # Show color preview
                st.markdown(f"""
                <div style="background-color: {color_options[selected_color]};
                            width: 30px;
                            height: 30px;
                            border-radius: 5px;
                            border: 1px solid #ddd;
                            margin-top: 5px;">
                </div>
                """, unsafe_allow_html=True)

                st.subheader("Additional Options")
                col1, col2 = st.columns(2)

                with col1:
                    led_lighting = st.checkbox(
                        "LED Lighting",
                        value=st.session_state.letter_properties.get("led_lighting", False),
                        key="input_led"
                    )

                    if led_lighting:
                        st.info("LED lighting adds illumination to your letters")

                with col2:
                    mounting_hardware = st.checkbox(
                        "Mounting Hardware",
                        value=st.session_state.letter_properties.get("mounting_hardware", False),
                        key="input_mounting"
                    )

                    if mounting_hardware:
                        st.info("Includes hardware for easy installation")

                installation = st.checkbox(
                    "Installation Service",
                    value=st.session_state.letter_properties.get("installation", False),
                    key="input_installation"
                )

                if installation:
                    st.info("Our team will professionally install your 3D letters")

                if letters.strip() and validate_inputs(height, width, depth, letters):
                    current_props = {
                        "material": material,
                        "height": height,
                        "width": width,
                        "depth": depth,
                        "quantity": quantity,
                        "num_letters": num_letters,
                        "finish": finish,
                        "led_lighting": led_lighting,
                        "mounting_hardware": mounting_hardware,
                        "installation": installation
                    }

                    estimate = calculate_costs(
                        material_options[material],
                        height, width, depth,
                        quantity * num_letters,
                        finish,
                        led_lighting,
                        mounting_hardware,
                        installation
                    )

                    st.metric(
                        "Estimated Total",
                        format_currency(estimate["total"]),
                        delta=None
                    )

                # --- 3D preview letter color map for this step ---
                letter_color_map = {}
                for i, letter in enumerate(letters.strip()):
                    letter_color_map[i] = color_options[selected_color]

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button(
                        "Calculate Quote",
                        use_container_width=True,
                        type="primary",
                        on_click=lambda: update_3d_preview(
                            st.session_state.letter_properties["letters"],
                            height,
                            width,
                            depth,
                            st.session_state.letter_properties["font"],
                            letter_color_map
                        )
                    )

                with col_btn2:
                    clear_form = st.form_submit_button("Clear Form", use_container_width=True)

                update_preview = st.form_submit_button(
                    "Update 3D Preview",
                    use_container_width=True,
                    on_click=lambda: update_3d_preview(
                        letters,
                        height,
                        width,
                        depth,
                        font,
                        letter_color_map
                    )
                )

            if submitted:
                st.session_state.letter_properties.update({
                    "material": material,
                    "height": height,
                    "width": width,
                    "depth": depth,
                    "quantity": quantity,
                    "finish": finish,
                    "led_lighting": led_lighting,
                    "mounting_hardware": mounting_hardware,
                    "installation": installation
                })

                if validate_inputs(height, width, depth, letters):
                    with st.spinner("Calculating quote..."):
                        costs = calculate_costs(
                            material_options[material],
                            height, width, depth,
                            quantity * num_letters,
                            finish,
                            led_lighting,
                            mounting_hardware,
                            installation
                        )

                        if quantity * num_letters >= 50:
                            discount_info = calculate_bulk_discount(costs["subtotal"], quantity * num_letters)
                            costs.update(discount_info)

                        volume = height * width * depth

                        delivery_days = calculate_delivery_time(
                            quantity * num_letters,
                            volume,
                            led_lighting,
                            installation
                        )

                        quotation = {
                            "letters": letters,
                            "font": font,
                            "material": material,
                            "dimensions": f"{height}\" x {width}\" x {depth}\"",
                            "height": height,
                            "width": width,
                            "depth": depth,
                            "quantity": quantity,
                            "total_letters": num_letters * quantity,
                            "finish": finish,
                            "volume_per_letter": volume,
                            "estimated_delivery_days": delivery_days,
                            "options": {
                                "LED Lighting": led_lighting,
                                "Mounting Hardware": mounting_hardware,
                                "Installation": installation
                            },
                            "costs": costs,
                            "led_lighting": led_lighting,
                            "mounting_hardware": mounting_hardware,
                            "installation": installation
                        }

                        # Only single color for all letters
                        quotation["letter_colors"] = letter_colors
                        quotation["multi_color"] = False
                        if letter_colors:
                            first_letter = letter_colors["0"]
                            quotation["color"] = first_letter["name"]
                            quotation["color_hex"] = first_letter["hex"]
                        else:
                            quotation["color"] = "Blue"
                            quotation["color_hex"] = "#2b5876"

                        st.session_state.current_quote = quotation

                        st.success("Quote calculated successfully!")

                        display_quotation(quotation)
                else:
                    st.error("Please check your inputs. Make sure dimensions are valid and text is not empty.")

            if clear_form:
                st.session_state.letter_properties = {
                    "letters": "LOGO",
                    "font": "helvetiker_bold",
                    "material": "Acrylic",
                    "height": 12.0,
                    "width": 8.0,
                    "depth": 2.0,
                    "quantity": 1,
                    "finish": "Standard",
                    "color": "Blue",
                    "color_hex": "#2b5876",
                    "multi_color": False,
                    "letter_colors": {},
                    "led_lighting": False,
                    "mounting_hardware": False,
                    "installation": False
                }
                st.session_state["step1_completed"] = False

                if "current_quote" in st.session_state:
                    del st.session_state.current_quote

                st.experimental_rerun()

            if update_preview:
                st.success("3D preview updated with all changes!")

        with preview_col:

            st.subheader("3D Letter Preview")

            preview_props = {
                "letters": letters,
                "height": height,
                "width": width,
                "depth": depth,
                "font": font,
                "material": material.lower(),
                "finish": finish
            }

            # All letters have the same color
            letter_color_map = {}
            for i, letter in enumerate(letters.strip()):
                letter_color_map[i] = color_options[selected_color]

            if letter_color_map:
                preview_props["letterColors"] = letter_color_map
                preview_props["multiColor"] = False
                preview_props["color"] = color_options[selected_color]
            else:
                preview_props["letterColors"] = {}
                preview_props["multiColor"] = False
                preview_props["color"] = "#2b5876"

            # --- Always update the 3D preview with the selected font ---
            update_3d_preview(
                letters,
                height,
                width,
                depth,
                font,
                letter_color_map
            )

            st.caption("Rotate with mouse drag. Zoom with scroll wheel. Font selection is reflected in the preview.")

            if st.button("Reset View", key="reset_preview"):
                st.markdown("""
                <script>
                    const iframe = document.querySelector('iframe');
                    if (iframe) {
                        iframe.contentWindow.postMessage({
                            type: 'reset_view'
                        }, '*');
                    }
                </script>
                """, unsafe_allow_html=True)
    else:
        st.info("Please enter your letters and choose a font, then click 'Next: Choose Options' to continue.")

def display_quotation(quotation: Dict[str, Any]) -> None:
    """Display a detailed breakdown of the quotation."""

    st.subheader("Quotation Details")

    tab_summary, tab_details, tab_export = st.tabs(["Summary", "Detailed Breakdown", "Export Options"])

    with tab_summary:
        st.markdown(f"**Order Summary for '{quotation['letters']}'**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Specifications")
            specs_data = [
                ["Material", quotation["material"]],
                ["Dimensions", quotation["dimensions"]],
                ["Font", quotation["font"]],
                ["Finish", quotation["finish"]],
                ["Quantity", f"{quotation['quantity']} sets ({quotation['total_letters']} letters)"]
            ]

            if quotation.get("multi_color", False):
                color_info = "Multiple colors"
            else:
                color_info = quotation.get("color", "Not specified")

            specs_data.append(["Color", color_info])

            specs_df = pd.DataFrame(specs_data, columns=["Specification", "Value"])
            st.dataframe(specs_df, hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### Options & Delivery")

            options_list = []
            for option, enabled in quotation["options"].items():
                status = "✅ Included" if enabled else "❌ Not included"
                options_list.append([option, status])

            options_list.append(["Estimated Delivery", f"{quotation['estimated_delivery_days']} business days"])

            options_df = pd.DataFrame(options_list, columns=["Option", "Status"])
            st.dataframe(options_df, hide_index=True, use_container_width=True)

        st.markdown("### Cost Summary")

        costs = quotation["costs"]
        costs_formatted = {
            "Material Cost": format_currency(costs["material_cost"]),
            "Finish Cost": format_currency(costs["finish_cost"]),
            "Options Cost": format_currency(costs["options_cost"]),
            "Subtotal": format_currency(costs["subtotal"])
        }

        if "discount_amount" in costs:
            costs_formatted["Bulk Discount"] = f"- {format_currency(costs['discount_amount'])} ({costs['discount_percentage']}%)"
            costs_formatted["After Discount"] = format_currency(costs["after_discount"])

        costs_formatted["Tax (10%)"] = format_currency(costs["tax"])
        costs_formatted["Total"] = format_currency(costs["total"])

        costs_df = pd.DataFrame(list(costs_formatted.items()), columns=["Item", "Amount"])
        st.dataframe(costs_df, hide_index=True, use_container_width=True)

        st.metric("Final Quote Amount", format_currency(costs["total"]))

        if st.button("Save This Quote", key="save_quote"):
            if "quotations" not in st.session_state:
                st.session_state.quotations = []

            st.session_state.quotations.append(quotation)
            st.success(f"Quote for '{quotation['letters']}' saved successfully!")

    with tab_details:
        st.markdown("### Detailed Cost Calculations")

        volume = quotation["volume_per_letter"]
        height, width = float(quotation["height"]), float(quotation["width"])
        area = height * width

        st.markdown(f"""
        #### Volume and Area Calculations
        - **Volume per letter**: {volume:.2f} cubic inches
        - **Area per letter**: {area:.2f} square inches
        - **Total volume**: {volume * quotation['total_letters']:.2f} cubic inches
        - **Total area**: {area * quotation['total_letters']:.2f} square inches
        """)

        material_rate = quotation["costs"]["material_cost"] / volume
        st.markdown(f"""
        #### Material Cost Breakdown
        - **Material**: {quotation["material"]}
        - **Rate**: {format_currency(material_rate)} per cubic inch
        - **Volume per letter**: {volume:.2f} cubic inches
        - **Cost per letter**: {format_currency(quotation["costs"]["material_cost"] / quotation['total_letters'])}
        - **Total material cost**: {format_currency(quotation["costs"]["material_cost"])}
        """)

        if quotation["costs"]["finish_cost"] > 0:
            finish_multiplier = quotation["costs"]["finish_cost"] / quotation["costs"]["material_cost"] + 1
            st.markdown(f"""
            #### Finish Cost Breakdown
            - **Finish type**: {quotation["finish"]}
            - **Price multiplier**: {finish_multiplier:.2f}x
            - **Total finish cost**: {format_currency(quotation["costs"]["finish_cost"])}
            """)
        else:
            st.markdown("#### Finish: Standard (No additional cost)")

        if quotation["costs"]["options_cost"] > 0:
            st.markdown("#### Options Cost Breakdown")
            options_breakdown = []

            if quotation["options"]["LED Lighting"]:
                led_cost = area * 15 * 1.2 * quotation['total_letters']
                options_breakdown.append(f"- **LED Lighting**: {format_currency(led_cost)}")

            if quotation["options"]["Mounting Hardware"]:
                hardware_cost = volume * 2 * quotation['total_letters']
                options_breakdown.append(f"- **Mounting Hardware**: {format_currency(hardware_cost)}")

            if quotation["options"]["Installation"]:
                installation_cost = area * 5 * quotation['total_letters']
                options_breakdown.append(f"- **Installation**: {format_currency(installation_cost)}")

            options_text = "\n".join(options_breakdown)
            st.markdown(f"""
            {options_text}
            - **Total options cost**: {format_currency(quotation["costs"]["options_cost"])}
            """)
        else:
            st.markdown("#### No additional options selected")

        if "discount_amount" in quotation["costs"]:
            st.markdown(f"""
            #### Bulk Discount
            - **Number of letters**: {quotation['total_letters']}
            - **Discount rate**: {quotation["costs"]["discount_percentage"]}%
            - **Discount amount**: {format_currency(quotation["costs"]["discount_amount"])}
            - **Subtotal after discount**: {format_currency(quotation["costs"]["after_discount"])}
            """)

        st.markdown(f"""
        #### Tax and Total
        - **Subtotal**: {format_currency(quotation["costs"]["subtotal"])}
        - **Tax (10%)**: {format_currency(quotation["costs"]["tax"])}
        - **Total**: {format_currency(quotation["costs"]["total"])}
        """)

    with tab_export:
        st.markdown("### Export Options")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export as CSV", key="export_csv"):
                with st.spinner("Generating CSV file..."):
                    csv_data = export_to_csv(quotation)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"quotation_{quotation['letters'].replace(' ', '_')}.csv",
                        mime="text/csv",
                        key="download_csv"
                    )

        with col2:
            if st.button("Export as PDF", key="export_pdf"):
                with st.spinner("Generating PDF file..."):
                    pdf_data = export_to_pdf(quotation)
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name=f"quotation_{quotation['letters'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key="download_pdf"
                    )


def initialize_letter_properties() -> None:
    """Initialize default letter properties in session state if not already present."""
    if "letter_properties" not in st.session_state:
        st.session_state.letter_properties = {
            "letters": "LOGO",
            "font": "helvetiker_bold",
            "material": "Acrylic",
            "height": 12.0,
            "width": 8.0,
            "depth": 2.0,
            "quantity": 1,
            "finish": "Standard",
            "color": "Blue",
            "color_hex": "#2b5876",
            "multi_color": False,
            "letter_colors": {},
            "led_lighting": False,
            "mounting_hardware": False,
            "installation": False
        }