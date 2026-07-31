"""
backend/utils

Shared utility functions for the MedSave backend.

Functions here are stateless helpers that do not depend on Flask
context, database connections, or application state.

Current utilities:
    calculate_savings_percent — compute savings between brand and generic price.
"""


def calculate_savings_percent(brand_price: float, generic_price: float) -> float:
    """
    Calculate the percentage saved by choosing a generic medicine
    over a branded equivalent.

    Args:
        brand_price:   MRP of the branded medicine in INR.
        generic_price: Jan Aushadhi price of the generic in INR.

    Returns:
        Savings as a percentage rounded to one decimal place.
        Returns 0.0 when brand_price is zero or negative to avoid
        division by zero.

    Example:
        calculate_savings_percent(35.0, 10.0) -> 71.4
    """
    if not brand_price or brand_price <= 0:
        return 0.0
    savings = ((brand_price - generic_price) / brand_price) * 100
    return round(savings, 1)
