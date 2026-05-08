import pandas as pd

def str_to_float_safe(texto):
    """Convert str to float, if it fails returns 0.0"""
    try:
        return float(texto)
    except (ValueError, TypeError):
        return 0.0

# Converter to preserve leading zeros and avoid '.0' when pandas casts numeric cells
def to_str_preserve(x):
    if pd.isna(x):
        return ''
    try:
        # Floats that are integers should be shown without .0
        if isinstance(x, float):
            if x.is_integer():
                return str(int(x))
            return str(x)
        return str(x)
    except Exception:
        return str(x)