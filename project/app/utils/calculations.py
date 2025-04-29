from typing import Dict, Any, Tuple, Union

def calculate_costs(material_info: Dict[str, float], height: float, width: float, 
                   depth: float, quantity: int, finish: str, led_lighting: bool, 
                   mounting_hardware: bool, installation: bool) -> Dict[str, float]:
    """
    Calculate costs for the 3D letter quotation.
    
    Args:
        material_info: Dictionary containing material rate
        height: Letter height in inches
        width: Letter width in inches
        depth: Letter depth in inches
        quantity: Total number of letters
        finish: Finish type
        led_lighting: Whether LED lighting is included
        mounting_hardware: Whether mounting hardware is included
        installation: Whether installation service is included
        
    Returns:
        Dictionary with cost breakdown
    """
    # Calculate basic measurements
    volume = height * width * depth
    area = height * width
    
    # Calculate material cost based on volume and material rate
    material_cost = volume * material_info["rate"]
    
    # Calculate finish costs
    finish_multipliers = {
        "Standard": 1.0,
        "Painted": 1.25,
        "High Gloss": 1.35,
        "Matte": 1.20
    }
    
    # Use default multiplier if finish type is not in the dictionary
    finish_multiplier = finish_multipliers.get(finish, 1.0)
    finish_cost = material_cost * (finish_multiplier - 1)
    
    # Calculate additional options
    options_cost = 0
    if led_lighting:
        options_cost += area * 15 * 1.2  # $15 per square inch for LED + 20% additional charge
    
    if mounting_hardware:
        options_cost += volume * 2  # $2 per cubic inch for hardware
    
    if installation:
        options_cost += area * 5  # $5 per square inch for installation
    
    # Calculate subtotal (per letter * quantity)
    per_letter_cost = material_cost + finish_cost
    options_total = options_cost * quantity
    subtotal = (per_letter_cost * quantity) + options_total
    
    # Calculate tax (10%)
    tax = subtotal * 0.1
    
    # Calculate total
    total = subtotal + tax
    
    return {
        "material_cost": material_cost * quantity,
        "finish_cost": finish_cost * quantity,
        "options_cost": options_total,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }

def calculate_bulk_discount(subtotal: float, quantity: int) -> Dict[str, Union[float, int]]:
    """
    Calculate bulk discount based on quantity.
    
    Args:
        subtotal: The subtotal amount before discount
        quantity: Total number of letters
        
    Returns:
        Dictionary with discount information
    """
    # Define discount tiers
    discount_tiers = [
        (100, 5),   # 5% discount for 100+ letters
        (250, 10),  # 10% discount for 250+ letters
        (500, 15),  # 15% discount for 500+ letters
        (1000, 20)  # 20% discount for 1000+ letters
    ]
    
    # Find the applicable discount percentage
    discount_percentage = 0
    for tier_quantity, tier_discount in discount_tiers:
        if quantity >= tier_quantity:
            discount_percentage = tier_discount
    
    # Calculate discount amount
    discount = subtotal * (discount_percentage / 100) if discount_percentage > 0 else 0
    
    # Return discount information
    return {
        "discount_percentage": discount_percentage,
        "discount": discount,
        "subtotal_after_discount": subtotal - discount
    }

def calculate_delivery_time(quantity: int, volume: float, 
                          led_lighting: bool, installation: bool) -> int:
    """
    Calculate estimated delivery time in business days.
    
    Args:
        quantity: Total number of letters
        volume: Volume per letter in cubic inches
        led_lighting: Whether LED lighting is included
        installation: Whether installation service is included
        
    Returns:
        Estimated delivery time in business days
    """
    # Base production time based on quantity
    if quantity <= 5:
        base_days = 3
    elif quantity <= 20:
        base_days = 5
    elif quantity <= 50:
        base_days = 7
    elif quantity <= 100:
        base_days = 10
    else:
        base_days = 14
    
    # Additional time based on complexity
    complexity_days = 0
    
    # Large volume letters take more time
    if volume > 500:
        complexity_days += 2
    elif volume > 200:
        complexity_days += 1
    
    # LED lighting adds time
    if led_lighting:
        complexity_days += 2
    
    # Installation service adds time for scheduling
    if installation:
        complexity_days += 1
    
    # Return total estimated days
    return base_days + complexity_days