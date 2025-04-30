def display_quotation_details(quote_idx: int) -> None:
    """Display detailed information for a specific quotation."""
    import requests
    from io import BytesIO

    # --- Helper: Download logo image from the internet and cache it in session_state ---
    LOGO_URL = "https://m.bbb.org/prod/ProfileImages/2023/7f0713a1-e873-4294-92c4-5d73261f6038.png"
    if "company_logo_bytes" not in st.session_state:
        try:
            response = requests.get(LOGO_URL)
            if response.status_code == 200:
                st.session_state.company_logo_bytes = response.content
            else:
                st.session_state.company_logo_bytes = None
        except Exception:
            st.session_state.company_logo_bytes = None

    # --- Helper: Patch export_to_pdf to add logo ---
    def export_to_pdf_with_logo(quote):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Draw the logo at the top left
        logo_bytes = st.session_state.get("company_logo_bytes", None)
        if logo_bytes:
            try:
                logo_img = ImageReader(BytesIO(logo_bytes))
                # Set logo size (width, height) in points
                logo_width = 80
                logo_height = 80
                c.drawImage(logo_img, 40, height - logo_height - 40, width=logo_width, height=logo_height, mask='auto')
            except Exception:
                pass  # If logo fails, just skip

        # Move down for the rest of the content
        y = height - 130

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"Quotation #{quote.get('id', '')}")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(40, y, f"Letters: {quote['letters']}")
        y -= 20
        c.drawString(40, y, f"Font: {quote.get('font', 'Default')}")
        y -= 20
        c.drawString(40, y, f"Material: {quote['material']}")
        y -= 20
        c.drawString(40, y, f"Dimensions: {quote['dimensions']}")
        y -= 20
        c.drawString(40, y, f"Sets of Letters: {quote['quantity']}")
        y -= 20
        c.drawString(40, y, f"Total Letters: {quote['total_letters']}")
        y -= 20
        c.drawString(40, y, f"Finish: {quote['finish']}")
        y -= 30

        # Color info
        if quote.get('multi_color', False):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Color Information:")
            y -= 20
            c.setFont("Helvetica", 12)
            for letter, color in quote['letter_colors'].items():
                c.drawString(50, y, f"Letter '{letter}': {color['name']} ({color['hex']})")
                y -= 18
        else:
            c.setFont("Helvetica", 12)
            c.drawString(40, y, f"Color: {quote['color']} ({quote['color_hex']})")
            y -= 20

        # Options
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Selected Options:")
        y -= 20
        c.setFont("Helvetica", 12)
        for option, selected in quote['options'].items():
            c.drawString(50, y, f"{option}: {'Yes' if selected else 'No'}")
            y -= 18

        # Cost breakdown
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Cost Breakdown:")
        y -= 20
        c.setFont("Helvetica", 12)
        costs = quote['costs']
        c.drawString(50, y, f"Material Cost: {format_currency(costs['material_cost'])}")
        y -= 18
        c.drawString(50, y, f"Finish Cost: {format_currency(costs['finish_cost'])}")
        y -= 18
        c.drawString(50, y, f"Options Cost: {format_currency(costs['options_cost'])}")
        y -= 18
        c.drawString(50, y, f"Subtotal: {format_currency(costs['subtotal'])}")
        y -= 18
        if costs.get('discount', 0) > 0:
            c.drawString(50, y, f"Bulk Discount ({costs['discount_percentage']}%): -{format_currency(costs['discount'])}")
            y -= 18
        c.drawString(50, y, f"Tax (10%): {format_currency(costs['tax'])}")
        y -= 18
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Final Total: {format_currency(costs['total'])}")
        y -= 24

        # Delivery time
        if 'estimated_delivery_days' in quote:
            delivery_days = quote['estimated_delivery_days']
            c.setFont("Helvetica", 12)
            c.drawString(40, y, f"Production Time: {delivery_days} business days")
            y -= 18

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()

    if 0 <= quote_idx < len(st.session_state.quotations):
        quote = st.session_state.quotations[quote_idx]
        
        # Display in an expander
        with st.expander("Quotation Details", expanded=True):
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Order Information")
                st.markdown(f"**Quotation #:** {quote_idx + 1}")
                st.markdown(f"**Letters:** {quote['letters']}")
                st.markdown(f"**Font:** {quote.get('font', 'Default')}")
                st.markdown(f"**Material:** {quote['material']}")
                st.markdown(f"**Dimensions:** {quote['dimensions']}")
                st.markdown(f"**Sets of Letters:** {quote['quantity']}")
                st.markdown(f"**Total Letters:** {quote['total_letters']}")
                st.markdown(f"**Finish:** {quote['finish']}")
                
                # Display color information
                if quote.get('multi_color', False):
                    st.markdown("### Color Information")
                    for letter, color in quote['letter_colors'].items():
                        st.markdown(f"- Letter '{letter}': <span style='color:{color['hex']}'>\u25A0</span> {color['name']}", unsafe_allow_html=True)
                else:
                    st.markdown(f"**Color:** <span style='color:{quote['color_hex']}'>\u25A0</span> {quote['color']}", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Options & Pricing")
                # Display selected options
                st.markdown("**Selected Options:**")
                for option, selected in quote['options'].items():
                    st.markdown(f"- {option}: {'Yes' if selected else 'No'}")
                
                # Cost breakdown
                st.markdown("### Cost Breakdown")
                costs = quote['costs']
                st.markdown(f"Material Cost: {format_currency(costs['material_cost'])}")
                st.markdown(f"Finish Cost: {format_currency(costs['finish_cost'])}")
                st.markdown(f"Options Cost: {format_currency(costs['options_cost'])}")
                st.markdown(f"**Subtotal:** {format_currency(costs['subtotal'])}")
                
                # Display discount if applicable
                if costs.get('discount', 0) > 0:
                    st.markdown(f"**Bulk Discount ({costs['discount_percentage']}%):** -{format_currency(costs['discount'])}")
                
                st.markdown(f"**Tax (10%):** {format_currency(costs['tax'])}")
                st.markdown(f"**Final Total:** {format_currency(costs['total'])}")
                
                # Display estimated delivery time
                if 'estimated_delivery_days' in quote:
                    delivery_days = quote['estimated_delivery_days']
                    delivery_date = datetime.now().strftime("%B %d, %Y")  # In a real app, calculate from saved date
                    st.markdown(f"**Production Time:** {delivery_days} business days")
        
        # Add export tab
        st.markdown("### Export Options")
        
        # Pre-generate the export data to avoid timing issues
        csv_data = export_to_csv(quote)
        pdf_data = export_to_pdf_with_logo(quote)  # Use the new function with logo

        # CSV download button
        st.download_button(
            label="Download Quotation as CSV",
            data=csv_data,
            file_name="quotation.csv",
            mime="text/csv"
        )
        
        # PDF download button
        st.download_button(
            label="Download Quotation as PDF",
            data=pdf_data,
            file_name="quotation.pdf",
            mime="application/pdf"
        )

        col1, col2 = st.columns(2)
        
        with col1:
            # Direct download button with pre-generated CSV data
            st.download_button(
                label="Export as CSV",
                data=csv_data,
                file_name=f"quotation_{quote['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key=f"download_csv_{quote_idx}",
                use_container_width=True,
                help="Download quote as CSV format for spreadsheets"
            )
        
        with col2:
            # Direct download button with pre-generated PDF data
            st.download_button(
                label="Export as PDF", 
                data=pdf_data,
                file_name=f"quotation_{quote['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{quote_idx}",
                use_container_width=True,
                help="Download quote as PDF document"
            )
