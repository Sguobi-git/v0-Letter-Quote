import pandas as pd
import io
from typing import Dict, Any, Union, List
import json
from datetime import datetime, timedelta
import streamlit as st


def export_to_csv(quotation: Dict[str, Any]) -> str:
    """
    Export quotation data to CSV format with improved error handling.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        CSV data as string
    """
    try:
        # Use safe string conversion for all values
        flat_data = {
            "Quotation Date": datetime.now().strftime("%Y-%m-%d"),
            "Letters": str(quotation.get('letters', 'N/A')),
            "Font": str(quotation.get('font', 'Default')),
            "Material": str(quotation.get('material', 'N/A')),
            "Dimensions": str(quotation.get('dimensions', 'N/A')),
            "Sets of Letters": str(quotation.get('quantity', 'N/A')),
            "Total Letters": str(quotation.get('total_letters', 'N/A')),
            "Finish": str(quotation.get('finish', 'N/A')),
            "Material Cost": f"{quotation.get('costs', {}).get('material_cost', 0):.2f}",
            "Finish Cost": f"{quotation.get('costs', {}).get('finish_cost', 0):.2f}",
            "Options Cost": f"{quotation.get('costs', {}).get('options_cost', 0):.2f}",
            "LED Lighting": "Yes" if quotation.get('options', {}).get('LED Lighting', False) else "No",
            "Mounting Hardware": "Yes" if quotation.get('options', {}).get('Mounting Hardware', False) else "No",
            "Installation": "Yes" if quotation.get('options', {}).get('Installation', False) else "No",
            "Subtotal": f"{quotation.get('costs', {}).get('subtotal', 0):.2f}",
            "Tax": f"{quotation.get('costs', {}).get('tax', 0):.2f}",
            "Total": f"{quotation.get('costs', {}).get('total', 0):.2f}"
        }
        
        # Add color information with safe handling
        if quotation.get('multi_color', False):
            flat_data["Color Mode"] = "Multi-Color"
            try:
                # Safely convert letter colors to JSON string
                flat_data["Letter Colors"] = json.dumps(quotation.get('letter_colors', {}))
            except:
                flat_data["Letter Colors"] = "(Color data unavailable)"
        else:
            flat_data["Color Mode"] = "Single Color"
            flat_data["Color"] = str(quotation.get('color', 'Default'))
        
        # Add discount information if present with safe handling
        costs = quotation.get('costs', {})
        if 'discount' in costs or 'discount_amount' in costs:
            discount_percentage = costs.get('discount_percentage', 0)
            discount_amount = costs.get('discount', costs.get('discount_amount', 0))
            flat_data["Discount Percentage"] = f"{discount_percentage}%"
            flat_data["Discount Amount"] = f"{discount_amount:.2f}"
        
        try:
            # Try pandas DataFrame approach
            df = pd.DataFrame([flat_data])
            return df.to_csv(index=False)
        except Exception as e:
            st.warning(f"Falling back to manual CSV generation: {e}")
            # Fallback to manual CSV creation if pandas fails
            csv_rows = [",".join(flat_data.keys())]
            csv_rows.append(",".join([f'"{str(v)}"' for v in flat_data.values()]))
            return "\n".join(csv_rows)
            
    except Exception as e:
        st.error(f"Error exporting to CSV: {e}")
        # Return a minimal CSV with error information
        return "Error,Message\nExport failed,Please try again"


def export_to_pdf(quotation: Dict[str, Any]) -> bytes:
    """
    Export quotation data to PDF format with improved error handling and fallbacks.
    Adds the company logo at the top of the PDF.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        PDF data as bytes
    """
    try:
        # Try using ReportLab
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        import os

        # Ensure we have valid data throughout
        costs = quotation.get('costs', {})
        options = quotation.get('options', {})
        
        # Create a PDF buffer
        buffer = BytesIO()
        
        # Set up the document with letter size paper
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        
        # Container for elements to build the PDF
        elements = []
        
        # Add company logo at the top
        logo_path = "project/app/static/images/original_logo.png"
        if os.path.exists(logo_path):
            try:
                # The logo is 400x400 px. To keep it clean and not crushed, set width and height to the same value,
                # and use preserveAspectRatio=True (default). Let's display it at 1.5 inch (about 144 px) width.
                # This will scale it down but keep it sharp and square.
                logo_display_size = 1.5 * inch  # 1.5 inch width and height
                logo = Image(logo_path, width=logo_display_size, height=logo_display_size, hAlign='CENTER')
                elements.append(logo)
                elements.append(Spacer(1, 0.2*inch))
            except Exception as img_err:
                st.warning(f"Could not add logo to PDF: {img_err}")
        else:
            st.warning(f"Logo file not found at {logo_path}. Skipping logo in PDF.")

        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Add title
        elements.append(Paragraph("3D Letter Quotation", title_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add date
        current_date = datetime.now().strftime('%B %d, %Y')
        elements.append(Paragraph(f"Date: {current_date}", normal_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Order Information
        elements.append(Paragraph("Order Information", subtitle_style))
        
        # Create order info table data
        info_data = [
            ["Letters:", str(quotation.get('letters', 'N/A'))],
            ["Font:", str(quotation.get('font', 'Default'))],
            ["Material:", str(quotation.get('material', 'N/A'))],
            ["Dimensions:", str(quotation.get('dimensions', 'N/A'))],
            ["Sets of Letters:", str(quotation.get('quantity', 'N/A'))],
            ["Total Letters:", str(quotation.get('total_letters', 'N/A'))],
            ["Finish:", str(quotation.get('finish', 'N/A'))]
        ]
        
        if quotation.get('multi_color', False):
            info_data.append(["Color Mode:", "Multi-Color"])
        else:
            info_data.append(["Color:", str(quotation.get('color', 'N/A'))])
        
        # Create and style the table
        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Selected Options
        elements.append(Paragraph("Selected Options", subtitle_style))
        
        options_data = []
        for option, selected in options.items():
            options_data.append([str(option) + ":", "Yes" if selected else "No"])
        
        # Make sure we have at least one option to display
        if not options_data:
            options_data = [["No options selected", ""]]
            
        options_table = Table(options_data, colWidths=[1.5*inch, 4*inch])
        options_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(options_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Cost Breakdown
        elements.append(Paragraph("Cost Breakdown", subtitle_style))
        
        costs_data = [
            ["Material Cost:", f"${costs.get('material_cost', 0):.2f}"],
            ["Finish Cost:", f"${costs.get('finish_cost', 0):.2f}"],
            ["Options Cost:", f"${costs.get('options_cost', 0):.2f}"],
            ["Subtotal:", f"${costs.get('subtotal', 0):.2f}"]
        ]
        
        # Add discount if available - check both key names for compatibility
        discount_key = None
        if 'discount' in costs:
            discount_key = 'discount'
        elif 'discount_amount' in costs:
            discount_key = 'discount_amount'
            
        if discount_key:
            discount_percentage = costs.get('discount_percentage', 0)
            discount_amount = costs.get(discount_key, 0)
            costs_data.append([f"Bulk Discount ({discount_percentage}%):", f"-${discount_amount:.2f}"])
            
            # Check for after_discount key, otherwise calculate
            if 'after_discount' in costs:
                costs_data.append(["After Discount:", f"${costs.get('after_discount', 0):.2f}"])
        
        costs_data.extend([
            ["Tax (10%):", f"${costs.get('tax', 0):.2f}"],
            ["Total:", f"${costs.get('total', 0):.2f}"]
        ])
        
        costs_table = Table(costs_data, colWidths=[2.5*inch, 3*inch])
        costs_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Bold font for total
        ]))
        
        elements.append(costs_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Delivery information if available
        if 'estimated_delivery_days' in quotation:
            elements.append(Paragraph("Delivery Information", subtitle_style))
            
            # Calculate delivery date
            delivery_days = quotation['estimated_delivery_days']
            delivery_date = (datetime.now() + timedelta(days=delivery_days)).strftime("%B %d, %Y")
            
            delivery_data = [
                ["Production Time:", f"{delivery_days} business days"],
                ["Estimated Completion:", delivery_date]
            ]
            
            delivery_table = Table(delivery_data, colWidths=[1.5*inch, 4*inch])
            delivery_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(delivery_table)
            elements.append(Spacer(1, 0.5*inch))
        
        # Thank you message
        thank_you_style = ParagraphStyle(
            'Thank You',
            parent=styles['Italic'],
            alignment=1,  # Center alignment
        )
        elements.append(Paragraph("Thank you for your business!", thank_you_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF value from the buffer
        pdf_value = buffer.getvalue()
        buffer.close()
        
        return pdf_value
        
    except ImportError as import_err:
        # Catch specific import error for ReportLab
        st.warning(f"ReportLab not available: {import_err}. Falling back to text output.")
        return _create_text_pdf_fallback(quotation)
        
    except Exception as reportlab_error:
        # Log the ReportLab error
        st.warning(f"ReportLab PDF generation failed: {reportlab_error}. Falling back to text output.")
        return _create_text_pdf_fallback(quotation)


def _create_text_pdf_fallback(quotation: Dict[str, Any]) -> bytes:
    """
    Create a simple text-based fallback when PDF generation fails.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        Text file content as bytes
    """
    buffer = io.BytesIO()
    
    try:
        current_date = datetime.now().strftime('%B %d, %Y')
        text_content = [
            "3D LETTER QUOTATION",
            "=" * 50,
            f"Date: {current_date}",
            "",
            "ORDER INFORMATION:",
            "-" * 50,
            f"Letters: {quotation.get('letters', 'N/A')}",
            f"Font: {quotation.get('font', 'Default')}",
            f"Material: {quotation.get('material', 'N/A')}",
            f"Dimensions: {quotation.get('dimensions', 'N/A')}",
            f"Sets of Letters: {quotation.get('quantity', 'N/A')}",
            f"Total Letters: {quotation.get('total_letters', 'N/A')}",
            f"Finish: {quotation.get('finish', 'N/A')}",
        ]
        
        if quotation.get('multi_color', False):
            text_content.append("Color Mode: Multi-Color")
        else:
            text_content.append(f"Color: {quotation.get('color', 'N/A')}")
        
        text_content.extend([
            "",
            "SELECTED OPTIONS:",
            "-" * 50
        ])
        
        options = quotation.get('options', {})
        if options:
            for option, selected in options.items():
                text_content.append(f"{option}: {'Yes' if selected else 'No'}")
        else:
            text_content.append("No options selected")
        
        costs = quotation.get('costs', {})
        text_content.extend([
            "",
            "COST BREAKDOWN:",
            "-" * 50,
            f"Material Cost: ${costs.get('material_cost', 0):.2f}",
            f"Finish Cost: ${costs.get('finish_cost', 0):.2f}",
            f"Options Cost: ${costs.get('options_cost', 0):.2f}",
            f"Subtotal: ${costs.get('subtotal', 0):.2f}"
        ])
        
        # Check for both possible discount keys
        if 'discount' in costs or 'discount_amount' in costs:
            discount_percentage = costs.get('discount_percentage', 0)
            discount_amount = costs.get('discount', costs.get('discount_amount', 0))
            text_content.append(f"Bulk Discount ({discount_percentage}%): -${discount_amount:.2f}")
            
            if 'after_discount' in costs:
                text_content.append(f"After Discount: ${costs.get('after_discount', 0):.2f}")
        
        text_content.extend([
            f"Tax (10%): ${costs.get('tax', 0):.2f}",
            f"TOTAL: ${costs.get('total', 0):.2f}",
            ""
        ])
        
        if 'estimated_delivery_days' in quotation:
            delivery_days = quotation['estimated_delivery_days']
            delivery_date = (datetime.now() + timedelta(days=delivery_days)).strftime("%B %d, %Y")
            
            text_content.extend([
                "DELIVERY INFORMATION:",
                "-" * 50,
                f"Production Time: {delivery_days} business days",
                f"Estimated Completion: {delivery_date}",
                ""
            ])
        
        text_content.append("Thank you for your business!")
        
        # Join the text content with line breaks
        content = "\n".join(text_content)
        
        # Write to buffer
        buffer.write(content.encode('utf-8'))
        
    except Exception as text_error:
        # If even the text fallback fails, provide error message
        error_message = f"Error generating document: {str(text_error)}\nPlease try again."
        buffer.write(error_message.encode('utf-8'))
    
    # Get the value and close the buffer
    value = buffer.getvalue()
    buffer.close()
    
    return value
