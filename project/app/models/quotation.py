from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class QuotationCosts:
    """Data class representing cost breakdown for a quotation."""
    material_cost: float
    finish_cost: float
    options_cost: float
    subtotal: float
    tax: float
    total: float
    discount: float = 0.0
    discount_percentage: int = 0

@dataclass
class QuotationOptions:
    """Data class representing optional add-ons for a quotation."""
    led_lighting: bool = False
    mounting_hardware: bool = False
    installation: bool = False

@dataclass
class ColorInfo:
    """Data class representing color information."""
    name: str
    hex: str

@dataclass
class Quotation:
    """Data class representing a complete quotation."""
    # Basic information
    letters: str
    material: str
    dimensions: str
    quantity: int
    total_letters: int
    finish: str
    volume_per_letter: float
    
    # Options and costs
    options: QuotationOptions
    costs: QuotationCosts
    
    # Color information
    multi_color: bool = False
    color: Optional[str] = None
    color_hex: Optional[str] = None
    letter_colors: Dict[str, ColorInfo] = field(default_factory=dict)
    
    # Additional information
    font: str = "default"
    estimated_delivery_days: int = 7
    created_at: datetime = field(default_factory=datetime.now)
    quote_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))
    
    @property
    def estimated_delivery_date(self) -> datetime:
        """Calculate the estimated delivery date."""
        return self.created_at + timedelta(days=self.estimated_delivery_days)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quotation':
        """Create a Quotation instance from a dictionary."""
        # Extract costs data
        costs_data = data.get('costs', {})
        costs = QuotationCosts(
            material_cost=costs_data.get('material_cost', 0.0),
            finish_cost=costs_data.get('finish_cost', 0.0),
            options_cost=costs_data.get('options_cost', 0.0),
            subtotal=costs_data.get('subtotal', 0.0),
            tax=costs_data.get('tax', 0.0),
            total=costs_data.get('total', 0.0),
            discount=costs_data.get('discount', 0.0),
            discount_percentage=costs_data.get('discount_percentage', 0)
        )
        
        # Extract options data
        options_data = data.get('options', {})
        options = QuotationOptions(
            led_lighting=options_data.get('LED Lighting', False),
            mounting_hardware=options_data.get('Mounting Hardware', False),
            installation=options_data.get('Installation', False)
        )
        
        # Process color information
        multi_color = data.get('multi_color', False)
        letter_colors = {}
        
        if multi_color and 'letter_colors' in data:
            for letter, color_info in data['letter_colors'].items():
                if isinstance(color_info, dict) and 'name' in color_info and 'hex' in color_info:
                    letter_colors[letter] = ColorInfo(
                        name=color_info['name'],
                        hex=color_info['hex']
                    )
        
        # Create and return Quotation instance
        return cls(
            letters=data.get('letters', ''),
            material=data.get('material', ''),
            dimensions=data.get('dimensions', ''),
            quantity=data.get('quantity', 0),
            total_letters=data.get('total_letters', 0),
            finish=data.get('finish', ''),
            volume_per_letter=data.get('volume_per_letter', 0.0),
            options=options,
            costs=costs,
            multi_color=multi_color,
            color=data.get('color'),
            color_hex=data.get('color_hex'),
            letter_colors=letter_colors,
            font=data.get('font', 'default'),
            estimated_delivery_days=data.get('estimated_delivery_days', 7)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Quotation instance to a dictionary."""
        result = {
            'letters': self.letters,
            'material': self.material,
            'dimensions': self.dimensions,
            'quantity': self.quantity,
            'total_letters': self.total_letters,
            'finish': self.finish,
            'volume_per_letter': self.volume_per_letter,
            'options': {
                'LED Lighting': self.options.led_lighting,
                'Mounting Hardware': self.options.mounting_hardware,
                'Installation': self.options.installation
            },
            'costs': {
                'material_cost': self.costs.material_cost,
                'finish_cost': self.costs.finish_cost,
                'options_cost': self.costs.options_cost,
                'subtotal': self.costs.subtotal,
                'tax': self.costs.tax,
                'total': self.costs.total,
                'discount': self.costs.discount,
                'discount_percentage': self.costs.discount_percentage
            },
            'multi_color': self.multi_color,
            'color': self.color,
            'color_hex': self.color_hex,
            'font': self.font,
            'estimated_delivery_days': self.estimated_delivery_days,
            'created_at': self.created_at.isoformat(),
            'quote_id': self.quote_id
        }
        
        if self.multi_color:
            result['letter_colors'] = {
                letter: {'name': color_info.name, 'hex': color_info.hex}
                for letter, color_info in self.letter_colors.items()
            }
            
        return result
    
    def calculate_estimated_delivery_days(self) -> int:
        """
        Calculate estimated delivery days based on complexity of the order.
        
        Returns:
            int: Estimated delivery days
        """
        base_days = 5  # Base production time
        
        # Add days based on quantity
        if self.quantity > 10:
            base_days += 2
        elif self.quantity > 5:
            base_days += 1
            
        # Add days for special options
        if self.options.led_lighting:
            base_days += 2
        if self.options.installation:
            base_days += 1
            
        # Add days for multi-color configuration
        if self.multi_color:
            base_days += len(self.letter_colors) // 2
            
        return base_days

    def apply_bulk_discount(self) -> None:
        """Apply bulk discount based on order quantity and update costs."""
        discount_percentage = 0
        
        # Calculate discount percentage based on quantity and total letters
        if self.quantity >= 10 or self.total_letters >= 100:
            discount_percentage = 10
        elif self.quantity >= 5 or self.total_letters >= 50:
            discount_percentage = 5
            
        # Apply discount
        if discount_percentage > 0:
            discount_amount = self.costs.subtotal * (discount_percentage / 100)
            self.costs.discount = discount_amount
            self.costs.discount_percentage = discount_percentage
            
            # Recalculate total
            discounted_subtotal = self.costs.subtotal - discount_amount
            self.costs.tax = discounted_subtotal * 0.1
            self.costs.total = discounted_subtotal + self.costs.tax