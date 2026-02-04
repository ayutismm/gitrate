from datetime import datetime

def calculate_account_age_years(created_at: str) -> float:
    """Calculate account age in years from ISO date string"""
    try:
        created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now(created_date.tzinfo)
        delta = now - created_date
        return round(delta.days / 365.25, 2)
    except:
        return 0

def format_number(num: int) -> str:
    """Format large numbers for display (e.g., 1500 -> 1.5K)"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def get_tier_color(tier: str) -> str:
    """Get color code for tier"""
    colors = {
        "Elite": "#FFD700",      # Gold
        "Advanced": "#C0C0C0",   # Silver
        "Intermediate": "#CD7F32", # Bronze
        "Beginner": "#87CEEB"    # Sky Blue
    }
    return colors.get(tier, "#808080")
