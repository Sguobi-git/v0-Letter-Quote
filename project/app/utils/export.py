import pandas as pd
import io
from typing import Dict, Any, Union, List
import json
from datetime import datetime

def export_to_csv(quotation: Dict[str, Any]) -> str:
    """
    Export quotation data to CSV format.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        CSV data as string
    """
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

def export_to_pdf(quotation: Dict[str, Any]) -> bytes:
    """
    Export quotation data to PDF format.
    
    Args:
        quotation: Quotation data dictionary
        
    Returns:
        PDF data as bytes
    """
    try:
        # We'll use FPDF library to create PDF
        from fpdf import FPDF
        
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", "B", 16)
        
        # Add title
        pdf.cell(0, 10, "3D Letter Quotation", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
        pdf.ln(5)
        
        # Add order information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Order Information", ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Order details
        info_items = [
            ["Letters:", quotation['letters']],
            ["Font:", quotation.get('font', 'Default')],
            ["Material:", quotation['material']],
            ["Dimensions:", quotation['dimensions']],
            ["Sets of Letters:", str(quotation['quantity'])],
            ["Total Letters:", str(quotation['total_letters'])],
            ["Finish:", quotation['finish']]
        ]
        
        # Add color information
        if quotation.get('multi_color', False):
            info_items.append(["Color Mode:", "Multi-Color"])
        else:
            info_items.append(["Color:", quotation['color']])
        
        # Print information items
        for label, value in info_items:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 8, label)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, value, ln=True)
        
        pdf.ln(5)
        
        # Add options information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Selected Options", ln=True)
        pdf.set_font("Arial", "", 12)
        
        for option, selected in quotation['options'].items():
            pdf.cell(50, 8, option + ":")
            pdf.cell(0, 8, "Yes" if selected else "No", ln=True)
        
        pdf.ln(5)
        
        # Add costs information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Cost Breakdown", ln=True)
        pdf.set_font("Arial", "", 12)
        
        costs_items = [
            ["Material Cost:", f"${quotation['costs']['material_cost']:.2f}"],
            ["Finish Cost:", f"${quotation['costs']['finish_cost']:.2f}"],
            ["Options Cost:", f"${quotation['costs']['options_cost']:.2f}"],
            ["Subtotal:", f"${quotation['costs']['subtotal']:.2f}"]
        ]
        
        # Add discount if applicable
        if 'discount' in quotation['costs']:
            discount_percentage = quotation['costs']['discount_percentage']
            discount_amount = quotation['costs']['discount']
            costs_items.append([f"Bulk Discount ({discount_percentage}%):", f"-${discount_amount:.2f}"])
        
        # Add tax and total
        costs_items.extend([
            ["Tax (10%):", f"${quotation['costs']['tax']:.2f}"],
            ["Total:", f"${quotation['costs']['total']:.2f}"]
        ])
        
        # Print costs items
        for label, value in costs_items:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 8, label)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, value, ln=True)
        
        # Add delivery information
        if 'estimated_delivery_days' in quotation:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Delivery Information", ln=True)
            pdf.set_font("Arial", "", 12)
            
            delivery_days = quotation['estimated_delivery_days']
            delivery_date = (datetime.now() + pd.Timedelta(days=delivery_days)).strftime("%B %d, %Y")
            
            pdf.cell(50, 8, "Production Time:")
            pdf.cell(0, 8, f"{delivery_days} business days", ln=True)
            
            pdf.cell(50, 8, "Estimated Completion:")
            pdf.cell(0, 8, delivery_date, ln=True)
        
        # Add footer
        pdf.ln(10)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "Thank you for your business!", ln=True, align="C")
        
        # Return the PDF as bytes
        return pdf.output(dest='S').encode('latin1')
    
    except ImportError:
        # If FPDF is not available, create a simple text representation
        output = io.StringIO()
        output.write("3D LETTER QUOTATION\n")
        output.write("===================\n\n")
        output.write(f"Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
        
        # Add basic information
        output.write("ORDER INFORMATION\n")
        output.write(f"Letters: {quotation['letters']}\n")
        output.write(f"Material: {quotation['material']}\n")
        output.write(f"Dimensions: {quotation['dimensions']}\n")
        output.write(f"Quantity: {quotation['total_letters']}\n")
        output.write(f"Finish: {quotation['finish']}\n\n")
        
        # Add cost information
        output.write("COST BREAKDOWN\n")
        output.write(f"Subtotal: ${quotation['costs']['subtotal']:.2f}\n")
        output.write(f"Tax: ${quotation['costs']['tax']:.2f}\n")
        output.write(f"Total: ${quotation['costs']['total']:.2f}\n")
        
        # Return as bytes
        return output.getvalue().encode('utf-8')