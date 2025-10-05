"""
Configuration settings for BudgetBot.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# App Settings
APP_NAME = os.getenv("APP_NAME", "BudgetBot")
APP_ICON = "💰"
CURRENCY_SYMBOL = "₹"
DEFAULT_USER_NAME = os.getenv("DEFAULT_USER_NAME", "User")

# Expense Categories
EXPENSE_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills", 
    "Entertainment", "Healthcare", "Education", "Rent", "Others"
]

# AI Settings
AI_MODEL = "gpt-4"
AI_TEMPERATURE = 0.7

# Budget Alert Thresholds (percentage)
WARNING_THRESHOLD = 80
DANGER_THRESHOLD = 100

# Chart Colors
CHART_COLORS = [
    '#667eea', '#764ba2', '#f093fb', '#4facfe',
    '#43e97b', '#fa709a', '#fee140', '#30cfd0'
]