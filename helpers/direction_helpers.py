'''Stateless utilities for directions'''

def deg_to_cardinal(degrees:str):
    """Convert degrees to nearest 16-point compass label."""
    try:
        deg = float(degrees)
        dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
        ix = int((deg + 11.25) / 22.5) % 16
        return dirs[ix]
    except Exception:
        return ""