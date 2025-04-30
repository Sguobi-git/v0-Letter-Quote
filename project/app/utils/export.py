import pandas as pd
import io
from typing import Dict, Any, Union, List
import json
from datetime import datetime

import streamlit as st

def export_to_csv(quotation: Dict[str, Any]) -> str:
    """
    Export quotation data to CSV format.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        CSV data as string
    """
    try:
        # Flatten the nested dictionary structure
        flat_data = {
            "Quotation Date": datetime.now().strftime("%Y-%m-%d"),
            "Letters": quotation['letters'],
            "Font": quotation.get('font', 'Default'),
            "Material": quotation['material'],
            "Dimensions": quotation['dimensions'],
            "Sets of Letters": quotation['quantity'],
            "Total Letters": quotation['total_letters'],
            "Finish": quotation['finish'],
            "Material Cost": quotation['costs']['material_cost'],
            "Finish Cost": quotation['costs']['finish_cost'],
            "Options Cost": quotation['costs']['options_cost'],
            "LED Lighting": quotation['options']['LED Lighting'],
            "Mounting Hardware": quotation['options']['Mounting Hardware'],
            "Installation": quotation['options']['Installation'],
            "Subtotal": quotation['costs']['subtotal'],
            "Tax": quotation['costs']['tax'],
            "Total": quotation['costs']['total']
        }
        
        # Add color information
        if quotation.get('multi_color', False):
            flat_data["Color Mode"] = "Multi-Color"
            # Convert letter colors to JSON string
            flat_data["Letter Colors"] = json.dumps(quotation['letter_colors'])
        else:
            flat_data["Color Mode"] = "Single Color"
            flat_data["Color"] = quotation['color']
        
        # Add discount information if present
        if 'discount' in quotation['costs']:
            flat_data["Discount Percentage"] = f"{quotation['costs']['discount_percentage']}%"
            flat_data["Discount Amount"] = quotation['costs']['discount']
        
        # Convert to DataFrame and then to CSV
        df = pd.DataFrame([flat_data])
        return df.to_csv(index=False)
    except Exception as e:
        st.error(f"Error exporting to CSV: {e}")
        return ""

def export_to_pdf(quotation: Dict[str, Any]) -> bytes:
    """
    Export quotation data to PDF format using ReportLab.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        PDF data as bytes
    """
    try:
        # Try using ReportLab which is more commonly available than FPDF
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        from datetime import datetime

        # Create a PDF buffer
        buffer = BytesIO()
        
        # Set up the document with letter size paper
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        
        # Container for elements to build the PDF
        elements = []
        
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
            ["Letters:", quotation['letters']],
            ["Font:", quotation.get('font', 'Default')],
            ["Material:", quotation['material']],
            ["Dimensions:", quotation['dimensions']],
            ["Sets of Letters:", str(quotation['quantity'])],
            ["Total Letters:", str(quotation['total_letters'])],
            ["Finish:", quotation['finish']]
        ]
        
        if quotation.get('multi_color', False):
            info_data.append(["Color Mode:", "Multi-Color"])
        else:
            info_data.append(["Color:", quotation['color']])
        
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
        for option, selected in quotation['options'].items():
            options_data.append([option + ":", "Yes" if selected else "No"])
        
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
            ["Material Cost:", f"${quotation['costs']['material_cost']:.2f}"],
            ["Finish Cost:", f"${quotation['costs']['finish_cost']:.2f}"],
            ["Options Cost:", f"${quotation['costs']['options_cost']:.2f}"],
            ["Subtotal:", f"${quotation['costs']['subtotal']:.2f}"]
        ]
        
        # Add discount if available
        if 'discount' in quotation['costs']:
            discount_percentage = quotation['costs']['discount_percentage']
            discount_amount = quotation['costs']['discount']
            costs_data.append([f"Bulk Discount ({discount_percentage}%):", f"-${discount_amount:.2f}"])
        
        costs_data.extend([
            ["Tax (10%):", f"${quotation['costs']['tax']:.2f}"],
            ["Total:", f"${quotation['costs']['total']:.2f}"]
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
            
            # Calculate delivery date based on business days (rough estimation)
            from datetime import timedelta
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
        
    except ImportError as e:
        # Fall back to a simpler method if ReportLab is not available
        import io
        from datetime import datetime, timedelta
        
        # Create a simple text-based "PDF" as a fallback
        buffer = io.BytesIO()
        
        # Write a simple text report
        current_date = datetime.now().strftime('%B %d, %Y')
        text_content = [
            "3D LETTER QUOTATION",
            "=" * 50,
            f"Date: {current_date}",
            "",
            "ORDER INFORMATION:",
            "-" * 50,
            f"Letters: {quotation['letters']}",
            f"Font: {quotation.get('font', 'Default')}",
            f"Material: {quotation['material']}",
            f"Dimensions: {quotation['dimensions']}",
            f"Sets of Letters: {quotation['quantity']}",
            f"Total Letters: {quotation['total_letters']}",
            f"Finish: {quotation['finish']}",
        ]
        
        if quotation.get('multi_color', False):
            text_content.append("Color Mode: Multi-Color")
        else:
            text_content.append(f"Color: {quotation['color']}")
        
        text_content.extend([
            "",
            "SELECTED OPTIONS:",
            "-" * 50
        ])
        
        for option, selected in quotation['options'].items():
            text_content.append(f"{option}: {'Yes' if selected else 'No'}")
        
        text_content.extend([
            "",
            "COST BREAKDOWN:",
            "-" * 50,
            f"Material Cost: ${quotation['costs']['material_cost']:.2f}",
            f"Finish Cost: ${quotation['costs']['finish_cost']:.2f}",
            f"Options Cost: ${quotation['costs']['options_cost']:.2f}",
            f"Subtotal: ${quotation['costs']['subtotal']:.2f}"
        ])
        
        if 'discount' in quotation['costs']:
            discount_percentage = quotation['costs']['discount_percentage']
            discount_amount = quotation['costs']['discount']
            text_content.append(f"Bulk Discount ({discount_percentage}%): -${discount_amount:.2f}")
        
        text_content.extend([
            f"Tax (10%): ${quotation['costs']['tax']:.2f}",
            f"TOTAL: ${quotation['costs']['total']:.2f}",
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
        
        # Get the value and close the buffer
        value = buffer.getvalue()
        buffer.close()
        
        return value
        
    except Exception as e:
        # Handle any other exceptions
        import io
        buffer = io.BytesIO()
        error_message = f"Error generating PDF: {str(e)}"
        buffer.write(error_message.encode('utf-8'))
        value = buffer.getvalue()
        buffer.close()
        return value
