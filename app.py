"""
BudgetBot - AI Financial Assistant
Modern Dark Theme Design
"""

import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import re

# ==================== CONFIGURATION ====================
APP_NAME = "BudgetBot"
APP_ICON = "💰"
EXPENSE_CATEGORIES = ['Rent', 'Food', 'Travel', 'Miscellaneous']
CURRENCY_SYMBOL = "$"

# ==================== HELPER FUNCTIONS ====================
def format_currency(amount):
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"

def get_emoji_for_category(category):
    return {
        'Rent': '🏠',
        'Food': '🍔',
        'Travel': '✈️',
        'Miscellaneous': '📦',
    }.get(category, '❓')

def get_time_ago(dt):
    now = datetime.now()
    if dt.date() == now.date():
        return dt.strftime('%I:%M %p').lstrip('0')
    return dt.strftime('%b %d')

def calculate_percentage(part, whole):
    if whole == 0:
        return 0
    return (part / whole) * 100

# ==================== MOCK SERVICES ====================
class MockOCRService:
    def process_receipt(self, image):
        return True, {'amount': 42.50, 'category': 'Food'}, None

class MockAIService:
    def __init__(self, categories):
        self.categories = categories
        self.category_mapping = {
            'groceries': 'Food', 'dinner': 'Food', 'uber': 'Travel', 
            'gas': 'Travel', 'movie': 'Miscellaneous', 'rent': 'Rent'
        }
        self.expense_pattern = re.compile(
            r"(?:spent|paid|bought).*?(\$?\s*[\d,]+\.?\d*)\s*(?:on|for)\s*(.*?)(?:\s|$)", 
            re.IGNORECASE
        )

    def _parse_expense_command(self, text):
        match = self.expense_pattern.search(text)
        if match:
            amount_str = match.group(1).replace('$', '').replace(',', '').strip()
            try:
                amount = float(amount_str)
            except ValueError:
                return None, None, None
            item_desc = match.group(2).strip()
            
            category = 'Miscellaneous'
            for key, budget_cat in self.category_mapping.items():
                if key in item_desc.lower():
                    category = budget_cat
                    break
            
            return amount, category, item_desc
        return None, None, None

    def _generate_expense_response(self, amount, category, current_spending, budget):
        remaining = budget - current_spending
        
        if budget == 0:
             percentage_str = "no budget set"
        elif remaining < 0:
            percentage_str = f"{abs(calculate_percentage(remaining, budget)):.0f}% over budget" 
        else:
            percentage_str = f"{calculate_percentage(remaining, budget):.0f}% remaining"

        response = (
            f"Got it! I've recorded ${amount:,.2f} for {category}. "
            f"You've spent ${current_spending:,.0f} out of your ${budget:,.0f} {category} budget this month. "
            f"You're doing great - {percentage_str}!"
        )
        return response

    def chat(self, user_input, expenses, budgets, income, spending_goal, savings_goal, chat_history):
        amount, category, item_desc = self._parse_expense_command(user_input)
        
        if amount and category:
            new_expense = {
                'amount': amount,
                'category': category,
                'description': item_desc,
                'date': datetime.now(),
            }
            
            current_category_spending = sum(e['amount'] for e in expenses if e['category'] == category)
            new_category_spending = current_category_spending + amount
            budget = budgets.get(category, 0.0)
            
            response_text = self._generate_expense_response(
                amount, category, new_category_spending, budget
            )
            
            return response_text, new_expense 
            
        else:
            return "I can help you track expenses! Try saying something like 'I spent $20 on coffee'", None

ocr_service = MockOCRService()
ai_service = MockAIService(EXPENSE_CATEGORIES)

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title=f"{APP_ICON} {APP_NAME}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Dark Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        padding: 0 1.5rem;
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Sidebar Cards */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .sidebar-card h3 {
        font-size: 0.875rem;
        font-weight: 500;
        opacity: 0.8;
        margin-bottom: 0.75rem;
    }
    
    .sidebar-card .big-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .sidebar-card .sub-info {
        display: flex;
        justify-content: space-between;
        font-size: 0.875rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);
    }
    
    /* Goal Cards */
    .goal-header {
        color: white;
        font-size: 1rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        opacity: 0.9;
    }
    
    .goal-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .goal-card:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-2px);
    }
    
    .goal-card .category-name {
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .goal-card .amount-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
    }
    
    .goal-card .status-text {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.8rem;
        text-align: right;
        margin-top: 0.5rem;
    }
    
    /* Main Content */
    .main-header {
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }
    
    .main-header p {
        color: #6b7280;
        font-size: 1rem;
    }
    
    /* Chat Messages */
    .chat-container {
        overflow-y: auto;
        padding: 0.5rem 0;
    }
    
    .bot-message {
        background: #f3f4f6;
        color: #1f2937;
        border-radius: 16px 16px 16px 4px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        max-width: 75%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px 16px 4px 16px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    /* Input Area */
    .input-container {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 24px;
        padding: 0.5rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-top: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div {
        border: none !important;
        background: transparent !important;
    }
    
    .stTextInput input {
        border: none !important;
        background: transparent !important;
        padding: 0.5rem 0 !important;
    }
    
    button[kind="secondary"] {
        background: none !important;
        border: none !important;
        color: #6b7280 !important;
        padding: 0.5rem !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Hide file uploader */
    [data-testid="stFileUploader"] {
        display: none !important;
    }
    
    /* Edit buttons */
    .edit-btn {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 1.1rem !important;
        padding: 0.25rem !important;
        cursor: pointer !important;
    }
    
    .edit-btn:hover {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'initialized' not in st.session_state:
    st.session_state.income = 2100.00
    st.session_state.savings_goal = 5000.00
    st.session_state.current_savings = 3200.00
    
    st.session_state.budgets = {
        'Rent': 1200.0,
        'Food': 400.0,
        'Travel': 300.0,
        'Miscellaneous': 200.0,
    }
    
    st.session_state.expenses = [
        {'amount': 1200.0, 'category': 'Rent', 'description': 'Monthly rent', 'date': datetime.now() - timedelta(days=5)},
        {'amount': 240.0, 'category': 'Food', 'description': 'Groceries', 'date': datetime.now() - timedelta(hours=5)},
        {'amount': 45.0, 'category': 'Food', 'description': 'Groceries today', 'date': datetime.now() - timedelta(minutes=10)}, 
        {'amount': 180.0, 'category': 'Travel', 'description': 'Train tickets', 'date': datetime.now() - timedelta(hours=2)},
        {'amount': 95.0, 'category': 'Miscellaneous', 'description': 'Subscription', 'date': datetime.now() - timedelta(hours=1)},
    ]
    
    st.session_state.chat_messages = [
        {'message': "Hello! I'm BudgetBot, your personal finance manager. Tell me about your spending, or upload a receipt!", 'is_user': False, 'timestamp': datetime.now() - timedelta(minutes=15)},
        {'message': "I spent $45 on groceries today", 'is_user': True, 'timestamp': datetime.now() - timedelta(minutes=10)},
        {'message': "Got it! I've recorded $45.00 for Food. You've spent $285 out of your $400 Food budget this month. You're doing great - 29% remaining!", 'is_user': False, 'timestamp': datetime.now() - timedelta(minutes=8)},
    ]
    
    st.session_state.initialized = True

def get_category_spending():
    totals = {}
    for exp in st.session_state.expenses:
        cat = exp['category']
        totals[cat] = totals.get(cat, 0) + exp['amount']
    return totals

# ==================== SIDEBAR ====================
with st.sidebar:
    # Monthly Overview
    total_spent = sum(e['amount'] for e in st.session_state.expenses)
    spending_pct = calculate_percentage(total_spent, st.session_state.income)
    
    st.markdown(f"""
    <div class="sidebar-card">
        <h3>💰 Monthly Overview</h3>
        <div class="big-number">{format_currency(total_spent)}</div>
        <div class="sub-info">
            <span>of {format_currency(st.session_state.income)}</span>
            <span>{spending_pct:.0f}%</span>
        </div>
        <div style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.1); margin-top: 1rem;">
            <div style="height: 100%; width: {min(spending_pct, 100)}%; border-radius: 4px; background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Savings Goal
    savings_pct = calculate_percentage(st.session_state.current_savings, st.session_state.savings_goal)
    to_go = st.session_state.savings_goal - st.session_state.current_savings
    
    st.markdown(f"""
    <div class="sidebar-card">
        <h3>🎯 Savings Goal</h3>
        <div class="big-number" style="font-size: 1.5rem;">{format_currency(st.session_state.current_savings)} / {format_currency(st.session_state.savings_goal)}</div>
        <div class="sub-info">
            <span>{format_currency(to_go)} to go</span>
            <span>{savings_pct:.0f}%</span>
        </div>
        <div style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.1); margin-top: 1rem;">
            <div style="height: 100%; width: {min(savings_pct, 100)}%; border-radius: 4px; background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Spending Goals
    st.markdown('<div class="goal-header">📈 Spending Goals</div>', unsafe_allow_html=True)
    
    category_spending = get_category_spending()
    
    for category, budget in st.session_state.budgets.items():
        spent = category_spending.get(category, 0)
        percentage = calculate_percentage(spent, budget)
        emoji = get_emoji_for_category(category)
        
        if percentage >= 100:
            status = "Over budget!"
            bar_color = "#ef4444"
        else:
            status = f"{100 - min(percentage, 100):.0f}% remaining"
            bar_color = "#00d4ff"

        col1, col2 = st.columns([10, 1])
        
        with col1:
            st.markdown(f"""
            <div class="goal-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.3rem; margin-right: 0.75rem;">{emoji}</span>
                    <div style="flex: 1;">
                        <div class="category-name">{category}</div>
                        <div class="amount-text">{format_currency(spent)} / {format_currency(budget)}</div>
                    </div>
                </div>
                <div style="height: 6px; border-radius: 3px; background: rgba(255,255,255,0.1); margin-bottom: 0.5rem;">
                    <div style="height: 100%; width: {min(percentage, 100)}%; border-radius: 3px; background: {bar_color};"></div>
                </div>
                <div class="status-text">{status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✏️", key=f"edit_{category}", help=f"Edit {category}"):
                st.session_state[f"editing_{category}"] = not st.session_state.get(f"editing_{category}", False)
        
        if st.session_state.get(f"editing_{category}", False):
            new_budget = st.number_input(f"Budget ($)", value=budget, step=50.0, key=f"inp_{category}")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Save", key=f"save_{category}"):
                    st.session_state.budgets[category] = new_budget
                    st.session_state[f"editing_{category}"] = False
                    st.rerun()
            with col_b:
                if st.button("Cancel", key=f"cancel_{category}"):
                    st.session_state[f"editing_{category}"] = False
                    st.rerun()

# ==================== MAIN CONTENT ====================
col_header, col_settings = st.columns([10, 1])

with col_header:
    st.markdown("""
    <div class="main-header">
        <h1>BudgetBot</h1>
        <p>Your personal finance manager</p>
    </div>
    """, unsafe_allow_html=True)

with col_settings:
    if st.button("⚙️", key="settings"):
        st.session_state.show_settings = not st.session_state.get('show_settings', False)

if st.session_state.get('show_settings', False):
    with st.expander("Settings", expanded=True):
        new_income = st.number_input("Monthly Income ($)", value=st.session_state.income, step=100.0)
        if st.button("Save"):
            st.session_state.income = new_income
            st.success("Updated!")
            st.session_state.show_settings = False
            st.rerun()

# Chat Messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat_messages:
    time_str = get_time_ago(msg['timestamp'])
    
    if msg['is_user']:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="user-message">
                {msg['message']}
                <div class="message-time">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start;">
            <div class="bot-message">
                {msg['message']}
                <div class="message-time">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input Bar
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

col_icon1, col_icon2, col_input, col_send = st.columns([0.5, 0.5, 8, 1])

with col_icon1:
    st.button("📸", key="cam")

with col_icon2:
    if st.button("📎", key="upload"):
        st.session_state.show_uploader = True

with col_input:
    user_input = st.text_input("Message", placeholder="Type your message...", label_visibility="collapsed", key="chat_input")

with col_send:
    send = st.button("Send", key="send", type="primary")

if st.session_state.get('show_uploader', False):
    uploaded = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg'], key="uploader")
    if uploaded:
        st.session_state.show_uploader = False
else:
    uploaded = None

# ==================== HANDLERS ====================
if send and user_input:
    st.session_state.chat_messages.append({
        'message': user_input,
        'is_user': True,
        'timestamp': datetime.now()
    })
    
    response, new_expense = ai_service.chat(
        user_input,
        st.session_state.expenses,
        st.session_state.budgets,
        st.session_state.income,
        0,
        st.session_state.savings_goal,
        st.session_state.chat_messages
    )
    
    if new_expense:
        st.session_state.expenses.append(new_expense)
    
    st.session_state.chat_messages.append({
        'message': response,
        'is_user': False,
        'timestamp': datetime.now()
    })
    
    st.rerun()

if uploaded:
    try:
        image = Image.open(uploaded)
        success, data, error = ocr_service.process_receipt(image)
        
        if success:
            st.session_state.expenses.append({
                'amount': data['amount'],
                'category': data['category'],
                'description': f"Receipt: {uploaded.name}",
                'date': datetime.now()
            })
            st.session_state.chat_messages.append({
                'message': f"Receipt processed: {format_currency(data['amount'])} for {data['category']}",
                'is_user': False,
                'timestamp': datetime.now()
            })
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")