def display_quotation_details(quote_idx: int) -> None:
    """Display detailed information for a specific quotation."""
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
        
        with tab_export:
            st.markdown("### Export Options")
            
            # Pre-generate the export data to avoid timing issues
            csv_data = export_to_csv(quotation)
            pdf_data = export_to_pdf(quotation)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Direct download button with pre-generated CSV data
                st.download_button(
                    label="Export as CSV",
                    data=csv_data,
                    file_name=f"quotation_{quotation['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_csv_export",
                    use_container_width=True,
                    help="Download quote as CSV format for spreadsheets"
                )
            
            with col2:
                # Direct download button with pre-generated PDF data
                st.download_button(
                    label="Export as PDF", 
                    data=pdf_data,
                    file_name=f"quotation_{quotation['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="download_pdf_export",
                    use_container_width=True,
                    help="Download quote as PDF document"
                )
