from typing import Union, Dict, Any

def format_currency(amount: float) -> str:
    """
    Format number as currency.
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"

def format_dimensions(height: float, width: float, depth: float) -> str:
    """
    Format dimensions for display.
    
    Args:
        height: Height in inches
        width: Width in inches
        depth: Depth in inches
        
    Returns:
        Formatted dimension string
    """
    return f"{height:.1f}\" × {width:.1f}\" × {depth:.1f}\""

def format_quotation_data(quotation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format quotation data for export or display.
    
    Args:
        quotation: Raw quotation data
        
    Returns:
        Formatted quotation data
    """
    # Create a formatted copy
    formatted = quotation.copy()
    
    # Format currency values
    costs = quotation['costs']
    formatted['costs'] = {
        'material_cost': format_currency(costs['material_cost']),
        'finish_cost': format_currency(costs['finish_cost']),
        'options_cost': format_currency(costs['options_cost']),
        'subtotal': format_currency(costs['subtotal']),
        'tax': format_currency(costs['tax']),
        'total': format_currency(costs['total'])
    }
    
    # Add discount if present
    if 'discount' in costs:
        formatted['costs']['discount'] = format_currency(costs['discount'])
        formatted['costs']['discount_percentage'] = f"{costs['discount_percentage']}%"
    
    return formatted