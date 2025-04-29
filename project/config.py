"""
Configuration settings for the 3D Letter Quotation Calculator application.
This file centralizes all configuration parameters to make them easily accessible and modifiable.
"""
import os
from pathlib import Path

# Application settings
APP_NAME = "3D Letter Quotation Calculator"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Calculate quotes for custom 3D letter signage"
COMPANY_NAME = "SignCraft 3D"
COMPANY_EMAIL = "info@signcraft3d.com"
COMPANY_PHONE = "+1 (555) 123-4567"
SUPPORT_EMAIL = "support@signcraft3d.com"

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FONTS_DIR = DATA_DIR / "fonts"
EXPORTS_DIR = BASE_DIR / "exports"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Materials database
MATERIALS = {
    "Acrylic": {
        "rate": 0.75,  # $ per cubic inch
        "description": "Lightweight and durable plastic material with excellent weather resistance.",
        "available_finishes": ["Standard", "Painted", "Mirrored", "Frosted"],
        "min_thickness": 0.5,  # inches
        "max_thickness": 2.0,  # inches
        "weight_per_cubic_inch": 0.04,  # pounds
        "lead_time_days": 5
    },
    "Aluminum": {
        "rate": 1.25,  # $ per cubic inch
        "description": "Lightweight metal with excellent corrosion resistance, ideal for outdoor use.",
        "available_finishes": ["Standard", "Painted", "Brushed", "Polished"],
        "min_thickness": 0.25,  # inches
        "max_thickness": 1.5,  # inches
        "weight_per_cubic_inch": 0.098,  # pounds
        "lead_time_days": 7
    },
    "Brass": {
        "rate": 2.50,  # $ per cubic inch
        "description": "Classic metal with a rich gold appearance that develops a patina over time.",
        "available_finishes": ["Standard", "Polished", "Antiqued", "Lacquered"],
        "min_thickness": 0.25,  # inches
        "max_thickness": 1.0,  # inches
        "weight_per_cubic_inch": 0.308,  # pounds
        "lead_time_days": 10
    },
    "Stainless Steel": {
        "rate": 2.00,  # $ per cubic inch
        "description": "Extremely durable and corrosion-resistant metal for long-lasting signage.",
        "available_finishes": ["Standard", "Brushed", "Mirrored", "Satin"],
        "min_thickness": 0.125,  # inches
        "max_thickness": 1.0,  # inches
        "weight_per_cubic_inch": 0.285,  # pounds
        "lead_time_days": 12
    },
    "Wood": {
        "rate": 0.50,  # $ per cubic inch
        "description": "Natural material with unique grain patterns for a warm, organic appearance.",
        "available_finishes": ["Standard", "Stained", "Painted", "Oiled"],
        "min_thickness": 0.75,  # inches
        "max_thickness": 3.0,  # inches
        "weight_per_cubic_inch": 0.02,  # pounds
        "lead_time_days": 6
    },
    "PVC": {
        "rate": 0.40,  # $ per cubic inch
        "description": "Economical and versatile plastic material suitable for indoor and outdoor use.",
        "available_finishes": ["Standard", "Painted", "Textured"],
        "min_thickness": 0.5,  # inches
        "max_thickness": 2.0,  # inches
        "weight_per_cubic_inch": 0.03,  # pounds
        "lead_time_days": 4
    }
}

# Finish options
FINISHES = {
    "Standard": {
        "multiplier": 1.0,
        "description": "Basic finish included with all materials"
    },
    "Painted": {
        "multiplier": 1.25,
        "description": "Custom color applied to the material surface"
    },
    "Brushed": {
        "multiplier": 1.30,
        "description": "Textured surface with fine linear patterns"
    },
    "Mirrored": {
        "multiplier": 1.40,
        "description": "Highly reflective surface treatment"
    },
    "Polished": {
        "multiplier": 1.35,
        "description": "Smooth, glossy surface with high reflectivity"
    },
    "Satin": {
        "multiplier": 1.25,
        "description": "Smooth surface with reduced glare"
    },
    "Frosted": {
        "multiplier": 1.30,
        "description": "Semi-transparent matte finish"
    },
    "Antiqued": {
        "multiplier": 1.40,
        "description": "Aged appearance with darker recesses"
    },
    "Stained": {
        "multiplier": 1.20,
        "description": "Colored finish that preserves wood grain"
    },
    "Oiled": {
        "multiplier": 1.15,
        "description": "Natural finish that enhances wood grain"
    },
    "Lacquered": {
        "multiplier": 1.25,
        "description": "Clear protective coating with slight gloss"
    },
    "Textured": {
        "multiplier": 1.20,
        "description": "Surface with tactile patterns"
    }
}

# Option pricing
OPTIONS = {
    "led_lighting": {
        "base_rate": 15.0,  # $ per square inch
        "multiplier": 1.2,
        "description": "Internal LED lighting for illuminated letters",
        "lead_time_days": 3
    },
    "mounting_hardware": {
        "base_rate": 2.0,  # $ per cubic inch
        "description": "Hardware for mounting letters to walls or surfaces",
        "lead_time_days": 1
    },
    "installation": {
        "base_rate": 5.0,  # $ per square inch
        "description": "Professional installation service",
        "lead_time_days": 7
    }
}

# Bulk discount tiers
BULK_DISCOUNTS = [
    {"min_quantity": 5, "discount_percentage": 5},
    {"min_quantity": 10, "discount_percentage": 10},
    {"min_quantity": 25, "discount_percentage": 15},
    {"min_quantity": 50, "discount_percentage": 20},
    {"min_quantity": 100, "discount_percentage": 25}
]

# Tax rate (percentage)
TAX_RATE = 10.0

# Authentication settings
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "signcraft3d"  # This should be changed in production
AUTH_COOKIE_NAME = "signcraft_auth"
AUTH_COOKIE_EXPIRY_DAYS = 30
AUTH_ENABLED = True  # Set to False to disable authentication

# Font settings
DEFAULT_FONT = "helvetiker_bold"
AVAILABLE_FONTS = [
    "helvetiker_bold",
    "helvetiker_regular",
    "optimer_bold",
    "optimer_regular",
    "gentilis_bold",
    "gentilis_regular"
]

# 3D viewer settings
VIEWER_DEFAULT_SETTINGS = {
    "letters": "LOGO",
    "height": 2.0,
    "depth": 0.6,
    "material": "plastic",
    "finish": "Standard",
    "color": "#3498db",
    "multiColor": False,
    "letterColors": {}
}

# Application theme
THEME_PRIMARY_COLOR = "#4568dc"
THEME_SECONDARY_COLOR = "#b06ab3"
THEME_ACCENT_COLOR = "#3498db"
THEME_TEXT_COLOR = "#333333"
THEME_BACKGROUND_COLOR = "#f8f9fa"