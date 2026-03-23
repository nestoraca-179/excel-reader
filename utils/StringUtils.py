def str_to_float_safe(texto):
    """Convert str to float, if it fails returns 0.0"""
    try:
        return float(texto)
    except (ValueError, TypeError):
        return 0.0