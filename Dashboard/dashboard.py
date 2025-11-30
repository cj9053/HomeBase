import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from decimal import Decimal

# Page configuration
st.set_page_config(
    page_title="Homebase Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for 12-point grid and styling
st.markdown("""
<style>
    /* 12-point grid system */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .welcome-text {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .homebase-name {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin: 0;
    }
    
    /* Menu toggle styling */
    .menu-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1f1f1f;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    
    /* Progress bar styling */
    .progress-container {
        margin-bottom: 1rem;
    }
    
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Transaction table styling */
    .transaction-row {
        padding: 0.75rem;
        border-bottom: 1px solid #f0f2f6;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .transaction-row:hover {
        background-color: #f8f9fa;
    }
    .t-category { color: #aaa; font-size: 0.9em; font-style: italic; }
    .t-date { color: #666; font-size: 0.8em; display: block; }

    
    /* Bill status badges */
    .status-pending {
        color: #ff9800;
        font-weight: 600;
    }
    
    .status-paid {
        color: #4CAF50;
        font-weight: 600;
    }
    
    .status-overdue {
        color: #f44336;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_database_connection():
    """Establish connection to MySQL database using secrets"""
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Data fetching functions
@st.cache_data(ttl=300)
def get_user_info(user_id):
    """Get user information"""
    # Convert to native Python int
    user_id = int(user_id)
    
    conn = get_database_connection()
    if conn:
        query = "SELECT username, email FROM Users WHERE user_id = %s"
        df = pd.read_sql(query, conn, params=(user_id,))
        return df.iloc[0] if not df.empty else None
    return None

@st.cache_data(ttl=300)
def get_household_info(user_id):
    """Get household information for user"""
    # Convert to native Python int
    user_id = int(user_id)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT h.household_id, h.name, hm.role
            FROM Households h
            JOIN HouseholdMembers hm ON h.household_id = hm.household_id
            WHERE hm.user_id = %s
            LIMIT 1
        """
        df = pd.read_sql(query, conn, params=(user_id,))
        return df.iloc[0] if not df.empty else None
    return None

@st.cache_data(ttl=300)
def get_all_users():
    """Get all users for master view toggle"""
    conn = get_database_connection()
    if conn:
        query = """
            SELECT u.user_id, u.username, u.email, h.name as household_name
            FROM Users u
            LEFT JOIN HouseholdMembers hm ON u.user_id = hm.user_id
            LEFT JOIN Households h ON hm.household_id = h.household_id
            ORDER BY u.user_id
        """
        df = pd.read_sql(query, conn)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_recent_transactions(household_id, days=365):
    """Get recent transactions for household"""
    # Convert numpy integers to native Python integers to avoid SQL conversion errors
    household_id = int(household_id)
    days = int(days)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT 
                t.transaction_id,
                t.amount,
                t.notes,
                t.created_at,
                u.username,
                c.name AS category,
                c.type AS category_type
            FROM Transactions t
            JOIN Users u ON t.user_id = u.user_id
            JOIN Categories c ON t.category_id = c.category_id
            WHERE t.household_id = %s 
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY t.created_at DESC
            LIMIT 10
        """
        df = pd.read_sql(query, conn, params=(household_id, days))
        return df
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_spending_data(household_id, user_id, period_days):
    """Get spending data for charts"""
    # Convert numpy integers to native Python integers to avoid SQL conversion errors
    household_id = int(household_id)
    user_id = int(user_id)
    period_days = int(period_days)
    
    conn = get_database_connection()
    if conn:
        # Total household spending by category
        total_query = """
            SELECT 
                c.name AS category,
                SUM(t.amount) AS total
            FROM Transactions t
            JOIN Categories c ON t.category_id = c.category_id
            WHERE t.household_id = %s 
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY c.name
        """
        total_df = pd.read_sql(total_query, conn, params=(household_id, period_days))
        
        # Average spending per user
        avg_query = """
            SELECT 
                u.username,
                AVG(t.amount) AS avg_amount
            FROM Transactions t
            JOIN Users u ON t.user_id = u.user_id
            WHERE t.household_id = %s 
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY u.username
            ORDER BY avg_amount DESC
            LIMIT 5
        """
        avg_df = pd.read_sql(avg_query, conn, params=(household_id, period_days))
        
        # User vs household spending
        user_vs_household_query = """
            SELECT 
                SUM(CASE WHEN t.user_id = %s THEN t.amount ELSE 0 END) AS my_spending,
                SUM(CASE WHEN t.user_id != %s THEN t.amount ELSE 0 END) AS household_spending
            FROM Transactions t
            WHERE t.household_id = %s 
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        comparison_df = pd.read_sql(user_vs_household_query, conn, 
                                    params=(user_id, user_id, household_id, period_days))
        
        return total_df, avg_df, comparison_df
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def get_upcoming_bills(household_id):
    """Get upcoming bills"""
    # Convert to native Python int
    household_id = int(household_id)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT 
                bill_id,
                name,
                amount,
                due_date,
                status
            FROM Bills
            WHERE household_id = %s
            AND due_date >= CURDATE()
            ORDER BY due_date ASC
            LIMIT 10
        """
        df = pd.read_sql(query, conn, params=(household_id,))
        return df
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_savings_goals(household_id):
    """Get savings goals"""
    # Convert to native Python int
    household_id = int(household_id)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT 
                goal_id,
                name,
                target_amount,
                current_amount,
                created_at
            FROM SavingsGoals
            WHERE household_id = %s
            ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn, params=(household_id,))
        return df
    return pd.DataFrame()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1  # Default user for demo
if 'show_menu' not in st.session_state:
    st.session_state.show_menu = False
if 'show_master_view' not in st.session_state:
    st.session_state.show_master_view = False

# Toggle menu function
def toggle_menu():
    st.session_state.show_menu = not st.session_state.show_menu

# Toggle master view function
def toggle_master_view():
    st.session_state.show_master_view = not st.session_state.show_master_view

# Master View Toggle (for demo purposes)
if st.sidebar.checkbox("🔧 Enable Master View (Demo)", value=st.session_state.show_master_view, key="master_view_toggle"):
    st.session_state.show_master_view = True
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👥 Switch User View")
    st.sidebar.caption("Select a user to view their dashboard")
    
    # Get all users
    all_users = get_all_users()
    
    if not all_users.empty:
        # Create user selection dropdown
        user_options = {}
        for idx, row in all_users.iterrows():
            label = f"{row['username']} ({row['email']})"
            if pd.notna(row['household_name']):
                label += f" - {row['household_name']}"
            user_options[label] = row['user_id']
        
        # Find current user label
        current_user_label = [label for label, uid in user_options.items() if uid == st.session_state.user_id]
        current_index = list(user_options.keys()).index(current_user_label[0]) if current_user_label else 0
        
        selected_user_label = st.sidebar.selectbox(
            "Select User",
            options=list(user_options.keys()),
            index=current_index,
            key="user_selector"
        )
        
        # Update user_id if selection changed
        selected_user_id = user_options[selected_user_label]
        if selected_user_id != st.session_state.user_id:
            st.session_state.user_id = selected_user_id
            st.cache_data.clear()
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.info(f"Currently viewing: **{selected_user_label.split(' (')[0]}**")
    else:
        st.sidebar.warning("No users found in database")
else:
    st.session_state.show_master_view = False

# Get user and household data
user_info = get_user_info(st.session_state.user_id)
household_info = get_household_info(st.session_state.user_id)

if user_info is None or household_info is None:
    st.error("Unable to load user or household information. Please check your database connection.")
    st.stop()

# Header Section
col_header_left, col_header_right = st.columns([9, 3])

with col_header_left:
    st.markdown(f'<p class="welcome-text">Welcome back, {user_info["username"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="homebase-name">{household_info["name"]}</h1>', unsafe_allow_html=True)

with col_header_right:
    if st.button("☰ Menu", key="menu_toggle", use_container_width=True):
        toggle_menu()
    
    # Side menu (when toggled)
    if st.session_state.show_menu:
        with st.container():
            st.markdown("---")
            st.write(f"**Account Details**")
            st.write(f"Username: {user_info['username']}")
            st.write(f"Email: {user_info['email']}")
            st.write(f"Role: {household_info['role']}")
            st.markdown("---")
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Time period selector for charts
col_title, col_period = st.columns([9, 3])
with col_title:
    st.markdown('<p class="section-title">Spending Overview</p>', unsafe_allow_html=True)
with col_period:
    period = st.selectbox(
        "Time Period",
        options=["Week", "Month", "Quarter", "Year"],
        index=1,
        label_visibility="collapsed"
    )

# Map period to days
period_days_map = {
    "Week": 7,
    "Month": 30,
    "Quarter": 90,
    "Year": 365
}
period_days = period_days_map[period]

# Get spending data
total_spending_df, avg_spending_df, comparison_df = get_spending_data(
    household_info['household_id'], 
    st.session_state.user_id, 
    period_days
)

# Three Donut Charts Section (4 columns each in 12-point grid)
chart_col1, chart_col2, chart_col3 = st.columns(3)

with chart_col1:
    st.markdown("#### Total Spending")
    if not total_spending_df.empty:
        fig1 = px.pie(
            total_spending_df, 
            values='total', 
            names='category',
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig1.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No spending data available for this period")

with chart_col2:
    st.markdown("#### Average Spending by User")
    if not avg_spending_df.empty:
        fig2 = px.pie(
            avg_spending_df, 
            values='avg_amount', 
            names='username',
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No spending data available for this period")

with chart_col3:
    st.markdown("#### My Spending vs Household")
    if not comparison_df.empty and comparison_df.iloc[0]['my_spending'] is not None:
        my_spend = float(comparison_df.iloc[0]['my_spending'] or 0)
        household_spend = float(comparison_df.iloc[0]['household_spending'] or 0)
        
        comparison_data = pd.DataFrame({
            'Category': ['My Spending', 'Others Spending'],
            'Amount': [my_spend, household_spend]
        })
        
        fig3 = px.pie(
            comparison_data, 
            values='Amount', 
            names='Category',
            hole=0.6,
            color_discrete_sequence=['#4CAF50', '#2196F3']
        )
        fig3.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No spending comparison data available")

st.markdown("<br>", unsafe_allow_html=True)

# Recent Transactions and Upcoming Bills Section
trans_col, bills_col = st.columns([6, 6])

with trans_col:
    st.markdown('<p class="section-title">Recent Transactions</p>', unsafe_allow_html=True)
    # Increase days to 365 to get more historical transactions
    transactions_df = get_recent_transactions(household_info['household_id'], days=365)
    with st.expander("Recent Transactions", expanded=False):
        if not transactions_df.empty:
            for index, row in transactions_df.iterrows():
                # Build your HTML string using f-strings
                html_row = f"""
                <div class="transaction-row">
                    <div>
                        <strong>{row['notes']}</strong>
                        <span class="t-date">by {row['username']} - {row['created_at']}</span>
                    </div>
                    <div style="text-align: right;">
                        <strong>${row['amount']:.2f}</strong>
                        <br>
                        <span class="t-category">{row['category']}</span>
                    </div>
                </div>
                """
                st.markdown(html_row, unsafe_allow_html=True)
        else:
            st.info("No recent transactions found.")
    
    # if not transactions_df.empty:
    #     for idx, row in transactions_df.iterrows():
    #         col1, col2, col3 = st.columns([3, 6, 3])
    #         with col1:
    #             st.write(f"**${row['amount']:.2f}**")
    #         with col2:
    #             st.write(f"{row['notes'] or row['category']}")
    #             st.caption(f"by {row['username']} - {row['created_at'].strftime('%b %d, %Y')}")
    #         with col3:
    #             st.write(f"_{row['category']}_")
    #         st.markdown("---")
    # else:
    #     st.info("No recent transactions found")

with bills_col:
    st.markdown('<p class="section-title">Upcoming Bills</p>', unsafe_allow_html=True)
    bills_df = get_upcoming_bills(household_info['household_id'])
    
    if not bills_df.empty:
        for idx, row in bills_df.iterrows():
            col1, col2, col3 = st.columns([4, 4, 4])
            with col1:
                st.write(f"**{row['name']}**")
            with col2:
                st.write(f"**${row['amount']:.2f}**")
            with col3:
                status_class = f"status-{row['status']}"
                st.markdown(f'<span class="{status_class}">{row["status"].upper()}</span>', unsafe_allow_html=True)
            st.caption(f"Due: {row['due_date'].strftime('%b %d, %Y')}")
            st.markdown("---")
    else:
        st.info("No upcoming bills found")

st.markdown("<br>", unsafe_allow_html=True)

# Savings Goals Section
st.markdown('<p class="section-title">Savings Goals</p>', unsafe_allow_html=True)
goals_df = get_savings_goals(household_info['household_id'])

if not goals_df.empty:
    # Display goals in 3 columns
    goals_cols = st.columns(3)
    
    for idx, row in goals_df.iterrows():
        col_idx = idx % 3
        with goals_cols[col_idx]:
            with st.container():
                st.markdown(f"**{row['name']}**")
                
                current = float(row['current_amount'])
                target = float(row['target_amount'])
                progress_pct = (current / target * 100) if target > 0 else 0
                
                st.progress(progress_pct / 100)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Current", f"${current:,.2f}")
                with col_b:
                    st.metric("Target", f"${target:,.2f}")
                
                st.caption(f"{progress_pct:.1f}% Complete")
                st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("No savings goals set for this household")
