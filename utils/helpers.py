"""
Helper utility functions.
"""

from datetime import datetime
from config.settings import CURRENCY_SYMBOL

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"

def get_emoji_for_category(category: str) -> str:
    """Get emoji for category"""
    emoji_map = {
        'Food': '🍽️',
        'Transport': '🚗',
        'Shopping': '🛍️',
        'Bills': '📄',
        'Entertainment': '🎬',
        'Healthcare': '🏥',
        'Education': '📚',
        'Rent': '🏠',
        'Others': '📦'
    }
    return emoji_map.get(category, '💰')

def get_time_ago(timestamp) -> str:
    """Get human-readable time difference"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except:
            return "Recently"
    
    diff = datetime.now() - timestamp
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{int(seconds/60)} min ago"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hrs ago"
    else:
        return f"{int(seconds/86400)} days ago"

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return (part / total) * 100