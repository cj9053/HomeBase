"""
HomeBase Dashboard - Frontend Application
This is the main Streamlit application file that handles UI rendering.
Database operations are in Dashboard/crud.py, business logic is in Dashboard/routes.py.
"""

import sys
import os

# Add Dashboard folder to path so we can import crud and routes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Dashboard'))

from streamlit_extras.stylable_container import stylable_container as sc
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import CRUD operations from Dashboard/crud.py
from crud import (
    get_database_connection, get_user_info, get_household_info,
    get_upcoming_bills, get_savings_goals, get_recent_transactions,
    get_spending_data, get_user_spending_data, get_household_members,
    get_categories, create_bill, check_and_update_overdue_bills,
    get_user_debt_settlements, create_category, delete_category,
    delete_savings_goal, pay_towards_goal, record_payment_to_user,
    user_has_household, get_all_users, add_member_to_household,
    create_household, create_user, get_all_households,
    get_or_create_permanent_category, mark_bill_as_paid, delete_bill
)

# Import route/business logic functions from Dashboard/routes.py
from routes import (
    is_admin, toggle_menu, toggle_master_view, onboarding_screen,
    show_add_bill_form, open_bill_action, handle_user_profile_update,
    render_master_view_selector
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Homebase Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================

st.markdown("""
    <style>
   #account-header-container {
    display: flex;             
    align-items: center;       
    gap: 15px;                 
    width: 100%;               
    margin-bottom: 5px;        
    }


    #account-header-container h3, #edit-button-wrapper {
        margin: 0;
        padding: 0;
    }



    #edit-button-wrapper > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); 
        background-color: white; 
    }


    div[data-testid="stExpander"] summary p {
        color: #1f1f1f !important; 
        font-weight: 600;
    }
    div[data-testid="stExpander"] summary p:hover {
        color: #1f1f1f !important; 
        font-weight: 600;
    }

   
   
   .stExpanderToggleIcon: hover{
        color: black;        
    }
    .stButton button {
        background-color: Orange;
        font-weight: bold;
        border: 2px solid black;
    }

    .stButton button:hover {
        background-color:transparent;
        color: Orange;
        border: 2px solid Orange;
    }
            
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
    .section-title:hover {
        background-color:transparent;
        color: black;
        border: transparent;
    }
    .streamlit-expanderHeader {
        background-color: white;
        color: black; 
            
    }
     .streamlit-expanderHeader:Hover {
        background-color: transparent;
        color: black; 
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
    
    /* Radio button styling */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div[data-testid="stMarkdownContainer"] > p {
        color: #1f1f1f;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: white;
        border-color: #ddd;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) > div:first-child {
        background-color: orange;
        border-color: orange;
    }
    
    /* Form submit button styling */
    .stFormSubmitButton button {
        background-color: Orange;
        font-weight: bold;
        border: 2px solid black;
        color: black;
    }
    
    .stFormSubmitButton button:hover {
        background-color: transparent;
        color: Orange;
        border: 2px solid Orange;
    }
    
    /* Goal achieved styling */
    .goal-achieved {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.1em;
    }
  
    
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

if 'household_info' not in st.session_state:
    if st.session_state.user_id is not None:
        household_data = get_household_info(st.session_state.user_id)
        if household_data is not None:
            st.session_state.household_info = {
                'household_id': household_data['household_id'], 
                'name': household_data['name'],
                'role': household_data['role'] 
            }
        else:
            st.session_state.household_info = None
    else:
        st.session_state.household_info = None

if 'show_menu' not in st.session_state:
    st.session_state.show_menu = False
if 'show_master_view' not in st.session_state:
    st.session_state.show_master_view = False
if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False


# ============================================================
# MASTER VIEW TOGGLE
# ============================================================

if st.sidebar.checkbox("🔧 Enable Master View (Demo)", value=st.session_state.show_master_view, key="master_view_toggle"):
    st.session_state.show_master_view = True
else:
    st.session_state.show_master_view = False

master_view_enabled = st.session_state.show_master_view
user_info = st.session_state.get("user_info", None)
household_info = st.session_state.get("household_info", None)


# ============================================================
# ONBOARDING CHECKS
# ============================================================

if not master_view_enabled:
    # Case 1: No profile created yet
    if user_info is None:
        onboarding_screen()
        st.stop()

    # Case 2: Profile exists but no household
    if user_info is not None and household_info is None:
        result = user_has_household(user_info["user_id"])
        if result is None:
            onboarding_screen()
            st.stop()
        else:
            st.session_state.household_info = {
                "household_id": result["household_id"],
                "role": result["role"],
                "name": None
            }


# ============================================================
# MASTER VIEW MODE
# ============================================================

if master_view_enabled:
    render_master_view_selector()

# Refresh user_info and household_info after potential changes
user_info = st.session_state.get('user_info', None)
household_info = st.session_state.get('household_info', None)

if user_info is None or household_info is None or household_info.get('household_id') is None:
    st.error("Unable to load user or household information. Please check your database connection.")
    st.stop()


# ============================================================
# HEADER SECTION
# ============================================================

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
            current_user_info = st.session_state.get('user_info', {})
            current_household_info = st.session_state.get('household_info', {})

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("""<h3 class="account-header-container">Account Details</h3>""", unsafe_allow_html=True)
            with col2:
                if st.button("Edit", key="edit_account_btn"):
                    st.session_state.show_edit_form = True

            st.write(f"Username: {current_user_info.get('username', 'N/A')}")
            st.write(f"Email: {current_user_info.get('email', 'N/A')}")
            st.write(f"Role: {current_household_info.get('role', 'N/A')}")
            st.markdown("---")
            
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

            if st.session_state.show_edit_form:
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📝 Edit User Information")

                with st.form("edit_user_form", clear_on_submit=False):
                    new_username = st.text_input("New Username", value=current_user_info['username'])
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save_submitted = st.form_submit_button("Save Changes")
                    
                    if save_submitted:
                        username_changed = new_username != st.session_state.user_info['username']
                        if username_changed:
                            if handle_user_profile_update(new_username):
                                st.success(f"Username successfully updated to **{new_username}**.")
                            else:
                                st.error("Failed to update username in the database.")
                        
                        if username_changed:
                            st.session_state.show_edit_form = False
                            st.rerun()
                    
                cancel_btn = st.button("Cancel", key="cancel_edit_btn_outside")
                if cancel_btn:
                    st.session_state.show_edit_form = False
                    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SPENDING OVERVIEW SECTION
# ============================================================

# Time period selector for charts
col_title, col_period = st.columns([9, 3])
with col_title:
    st.markdown('<h4 style="color: white;">Spending Overview</h4>', unsafe_allow_html=True)
with col_period:
    period = st.selectbox(
        "Time Period",
        options=["Week", "Month", "Quarter", "Year"],
        index=1,
        label_visibility="collapsed"
    )
    view_mode = st.radio(
        "Spending view",
        options=["My spending", "Household spending"],
        index=1,
        horizontal=True,
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

current_user_id = st.session_state.get("user_id")
current_household_id = household_info.get("household_id") if household_info else None

if current_user_id is None or current_household_id is None:
    st.info("Your profile is set up, but you are not yet linked to a household with spending data.")
    st.stop()

# Get spending data based on view mode
if view_mode == "My spending":
    user_category_df, user_avg_category_df, cumulative_df = get_user_spending_data(
        current_household_id,
        current_user_id,
        period_days
    )

    # Three Charts for My Spending View
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.markdown("#### My Total Spending")
        if not user_category_df.empty:
            total_amount = user_category_df['total'].sum()
            fig1 = px.pie(
                user_category_df, 
                values='total', 
                names='category',
                hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig1.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                annotations=[dict(text=f'${total_amount:.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            fig1.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No spending data available for this period")
    
    with chart_col2:
        st.markdown("#### My Average Spending by Category")
        if not user_avg_category_df.empty:
            avg_amount = user_avg_category_df['avg_amount'].mean()
            fig2 = px.pie(
                user_avg_category_df, 
                values='avg_amount', 
                names='category',
                hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                annotations=[dict(text=f'${avg_amount:.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            fig2.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No spending data available for this period")
    
    with chart_col3:
        st.markdown("#### Cumulative Spending Over Time")
        if not cumulative_df.empty:
            fig3 = px.line(
                cumulative_df, 
                x='date', 
                y='cumulative_total',
                markers=True
            )
            fig3.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                xaxis_title="Date",
                yaxis_title="Total ($)"
            )
            fig3.update_traces(line_color='#FF8C00')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No spending data available for this period")

else:
    total_spending_df, avg_spending_df, comparison_df = get_spending_data(
        current_household_id,
        current_user_id,
        period_days
    )

    # Three Donut Charts Section
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.markdown("#### Total Spending")
        if not total_spending_df.empty:
            total_amount = total_spending_df['total'].sum()
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
                margin=dict(t=0, b=0, l=0, r=0),
                annotations=[dict(text=f'${total_amount:.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            fig1.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No spending data available for this period")
    
    with chart_col2:
        st.markdown("#### Average Spending by User")
        if not avg_spending_df.empty:
            avg_amount = avg_spending_df['avg_amount'].mean()
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
                margin=dict(t=0, b=0, l=0, r=0),
                annotations=[dict(text=f'${avg_amount:.2f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            fig2.update_traces(textposition='inside', textinfo='percent')
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
            fig3.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No spending comparison data available")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PAY A HOUSEHOLD MEMBER SECTION
# ============================================================

st.markdown('<h4 style="color: white;">Pay a Household Member</h4>', unsafe_allow_html=True)

if 'show_payment_form' not in st.session_state:
    st.session_state.show_payment_form = False

if st.button("💸 Make a Payment", key="toggle_payment"):
    st.session_state.show_payment_form = not st.session_state.show_payment_form

if st.session_state.show_payment_form:
    household_members = get_household_members(household_info['household_id'])
    categories_df = get_categories(household_info['household_id'])
    
    # Filter out current user from receiver options
    receiver_options = household_members[household_members['user_id'] != st.session_state.user_id]
    
    if not receiver_options.empty:
        with st.form("payment_form"):
            st.markdown("### Record a payment")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a mapping of username to user_id
                receiver_dict = dict(zip(receiver_options['username'], receiver_options['user_id']))
                selected_receiver = st.selectbox(
                    "Pay to",
                    options=list(receiver_dict.keys())
                )
            
            with col2:
                payment_amount = st.number_input(
                    "Amount ($)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )
            
            # Category selection (mandatory) - only show shared categories for user-to-user payments
            if not categories_df.empty:
                # Filter to only 'shared' type categories - exclude 'bill' and 'goal'
                payment_categories = categories_df[categories_df['type'] == 'shared']
                
                if not payment_categories.empty:
                    category_dict = dict(zip(payment_categories['name'], payment_categories['category_id']))
                    selected_category = st.selectbox(
                        "Category *",
                        options=list(category_dict.keys()),
                        help="Select the category for this payment"
                    )
                    selected_category_id = category_dict[selected_category]
                else:
                    st.error("No shared expense categories found. Please create a shared category first.")
                    selected_category_id = None
            else:
                st.error("No categories found. Please create a category first.")
                selected_category_id = None
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit_payment = st.form_submit_button("Record Payment", use_container_width=True)
            with col_cancel:
                cancel_payment = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit_payment:
                if selected_category_id is None:
                    st.error("Please select a category.")
                else:
                    receiver_id = receiver_dict[selected_receiver]
                    success = record_payment_to_user(
                        household_info['household_id'],
                        st.session_state.user_id,
                        receiver_id,
                        payment_amount,
                        selected_category_id
                    )
                    if success:
                        st.success(f"Payment of ${payment_amount:.2f} to {selected_receiver} recorded!")
                        st.session_state.show_payment_form = False
                        get_user_debt_settlements.clear()
                        get_recent_transactions.clear()
                        st.rerun()
            
            if cancel_payment:
                st.session_state.show_payment_form = False
                st.rerun()
    else:
        st.info("No other household members found to pay.")

# Display debt settlements for the user
st.markdown("---")
debt_settlements = get_user_debt_settlements(household_info['household_id'], st.session_state.user_id)

with st.expander("💰 My Payment History", expanded=False):
    if not debt_settlements.empty:
        for index, row in debt_settlements.iterrows():
            # Determine if current user is payer or receiver
            is_payer = row['payer_user_id'] == st.session_state.user_id
            
            if is_payer:
                description = f"You paid {row['receiver_name']}"
                amount_color = "red"
                amount_prefix = "-"
            else:
                description = f"{row['payer_name']} paid you"
                amount_color = "green"
                amount_prefix = "+"
            
            status_class = f"status-{row['status']}"
            
            html_row = f"""
            <div class="transaction-row">
                <div>
                    <strong style="color: black;">{description}</strong>
                    <span class="t-date">{row['created_at']}</span>
                </div>
                <div style="text-align: right;">
                    <strong style="color: {amount_color};">{amount_prefix}${row['amount']:.2f}</strong>
                    <br>
                    <span class="{status_class}">{row['status'].upper()}</span>
                </div>
            </div>
            """
            st.markdown(html_row, unsafe_allow_html=True)
    else:
        st.info("No payment history found.")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# RECENT TRANSACTIONS SECTION
# ============================================================

st.markdown('<h4 style="color: white;">Recent Transactions</h4>', unsafe_allow_html=True)
transactions_df = get_recent_transactions(household_info['household_id'], days=365)

with st.expander("Recent Transactions", expanded=False):
    if not transactions_df.empty:
        for index, row in transactions_df.iterrows():
            html_row = f"""
            <div class="transaction-row">
                <div>
                    <strong style="color: black;">{row['notes']}</strong>
                    <span class="t-date">by {row['username']} - {row['created_at']}</span>
                </div>
                <div style="text-align: right;">
                    <strong style="color: red;">${row['amount']:.2f}</strong>
                    <br>
                    <span class="t-category">{row['category']}</span>
                </div>
            </div>
            """
            st.markdown(html_row, unsafe_allow_html=True)
    else:
        st.info("No recent transactions found.")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SAVINGS GOALS SECTION
# ============================================================

st.markdown('<h4 style="color: white;">Savings Goals</h4>', unsafe_allow_html=True)
goals_df = get_savings_goals(household_info['household_id'])

if not goals_df.empty:
    goals_cols = st.columns(3)
    
    for idx, row in goals_df.iterrows():
        col_idx = idx % 3
        with goals_cols[col_idx]:
            with st.container():
                goal_id = int(row["goal_id"])
                st.markdown(f"**{row['name']}**")
                
                current = float(row['current_amount'])
                target = float(row['target_amount'])
                progress_pct = (current / target * 100) if target > 0 else 0
                goal_achieved = current >= target
                
                # Use green progress bar if goal is achieved
                if goal_achieved:
                    st.markdown(
                        f'<div style="background-color: #4CAF50; height: 10px; border-radius: 5px; width: 100%;"></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.progress(progress_pct / 100)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Current", f"${current:,.2f}")
                with col_b:
                    st.metric("Target", f"${target:,.2f}")
                
                if goal_achieved:
                    st.markdown('<p class="goal-achieved">🎉 Goal Achieved!</p>', unsafe_allow_html=True)
                else:
                    st.caption(f"{progress_pct:.1f}% Complete")

                # Show buttons - only show Pay button if goal not achieved
                if goal_achieved:
                    # Only show delete button when goal is achieved (admin only)
                    if is_admin():
                        delete_clicked = st.button(
                            "Delete",
                            key=f"delete_goal_{goal_id}",
                            use_container_width=True
                        )
                    else:
                        delete_clicked = False
                    pay_clicked = False
                else:
                    # Show both Pay and Delete buttons for active goals
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        pay_clicked = st.button(
                            "➕ Pay",
                            key=f"pay_goal_{goal_id}",
                            use_container_width=True
                        )
                    
                    with btn_col2:
                        if is_admin():
                            delete_clicked = st.button(
                                "Delete",
                                key=f"delete_goal_{goal_id}",
                                use_container_width=True
                            )
                        else:
                            delete_clicked = False
                
                if pay_clicked:
                    st.session_state[f"show_payment_dialog_{goal_id}"] = True
                
                if st.session_state.get(f"show_payment_dialog_{goal_id}", False):
                    remaining = target - current
                    payment_amount = st.number_input(
                        f"Payment amount (max ${remaining:,.2f})",
                        min_value=0.01,
                        step=10.0,
                        format="%.2f",
                        key=f"payment_input_{goal_id}"
                    )
                    
                    is_valid_amount = payment_amount <= remaining
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submit_payment = st.button(
                            "Submit Payment", 
                            key=f"submit_payment_{goal_id}",
                            use_container_width=True,
                            disabled=not is_valid_amount
                        )
                    with col_cancel:
                        cancel_payment = st.button(
                            "Cancel", 
                            key=f"cancel_payment_{goal_id}",
                            use_container_width=True
                        )
                    
                    if submit_payment and is_valid_amount:
                        success, message = pay_towards_goal(goal_id, household_info["household_id"], payment_amount, st.session_state.user_id)
                        if success:
                            st.success(message)
                            get_savings_goals.clear()
                            get_recent_transactions.clear()
                            st.session_state[f"show_payment_dialog_{goal_id}"] = False
                            st.rerun()
                        else:
                            st.error(message)
                    
                    if cancel_payment:
                        st.session_state[f"show_payment_dialog_{goal_id}"] = False
                        st.rerun()
                
                if delete_clicked:
                    success = delete_savings_goal(goal_id, household_info["household_id"])
                    if success:
                        st.success("Savings goal deleted.")
                        get_savings_goals.clear()
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("No savings goals set for this household")

st.markdown("---")

# Toggle button for creating new savings goal (admin only)
if 'show_create_goal_form' not in st.session_state:
    st.session_state.show_create_goal_form = False

if is_admin():
    if st.button("➕ Create New Savings Goal", key="toggle_create_goal"):
        st.session_state.show_create_goal_form = not st.session_state.show_create_goal_form

if st.session_state.show_create_goal_form and is_admin():
    st.markdown("### Create a new savings goal")
    
    with st.form("create_savings_goal"):
        new_goal_name = st.text_input("Goal name")
        new_target_amount = st.number_input(
            "Target amount ($)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
        )

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            create_submitted = st.form_submit_button("Create goal", use_container_width=True)
        with col_cancel:
            cancel_create = st.form_submit_button("Cancel", use_container_width=True)
    
    if create_submitted:
        if not new_goal_name or new_target_amount <= 0:
            st.error("Please enter a goal name and a positive target amount.")
        else:
            conn = get_database_connection()
            if conn is None:
                st.error("Could not connect to database to create goal.")
            else:
                try:
                    cursor = conn.cursor()
                    insert_query = """
                        INSERT INTO SavingsGoals (household_id, name, target_amount, current_amount)
                        VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(
                        insert_query,
                        (int(household_info["household_id"]), new_goal_name, float(new_target_amount), 0.0),
                    )
                    conn.commit()
                    cursor.close()
                    st.success("Savings goal created successfully.")
                    get_savings_goals.clear()
                    st.session_state.show_create_goal_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating savings goal: {e}")
    
    if cancel_create:
        st.session_state.show_create_goal_form = False
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# UPCOMING BILLS SECTION
# ============================================================

check_and_update_overdue_bills(household_info['household_id'])
st.markdown('<h4 style="color: white;">Upcoming Bills</h4>', unsafe_allow_html=True)
bills_df = get_upcoming_bills(household_info['household_id'])

if not bills_df.empty:
    bills_cols = st.columns(3)
    
    for idx, row in bills_df.iterrows():
        col_idx = idx % 3
        with bills_cols[col_idx]:
            with st.container():
                bill_id = int(row["bill_id"])
                st.markdown(f"**{row['name']}**")
                
                amount = float(row['amount'])
                due_date = row['due_date']
                status = row['status']
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Amount", f"${amount:,.2f}")
                with col_b:
                    status_class = f"status-{status}"
                    st.markdown(f'<div style="padding-top: 10px;"><span class="{status_class}">{status.upper()}</span></div>', unsafe_allow_html=True)
                
                st.caption(f"Due: {due_date.strftime('%b %d, %Y')}")
                
                if st.button(
                    "Manage",
                    key=f"manage_bill_{bill_id}",
                    use_container_width=True
                ):
                    open_bill_action(bill_id, row['name'], amount)

                st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("No upcoming bills found")

st.markdown("---")

# Toggle button for creating new bill (admin only)
if 'show_create_bill_form' not in st.session_state:
    st.session_state.show_create_bill_form = False

if is_admin():
    if st.button("➕ Create New Bill", key="toggle_create_bill"):
        st.session_state.show_create_bill_form = not st.session_state.show_create_bill_form

if st.session_state.show_create_bill_form and is_admin():
    st.markdown("### Create a new bill")
    
    with st.form("create_bill_form"):
        col1, col2 = st.columns(2)
        with col1:
            bill_name = st.text_input("Bill Name", placeholder="e.g. Internet, Rent")
        with col2:
            bill_amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        
        bill_due_date = st.date_input("Due Date")
        
        col_submit, col_cancel = st.columns(2)
        with col_submit:
            bill_submitted = st.form_submit_button("Create Bill", use_container_width=True)
        with col_cancel:
            cancel_bill = st.form_submit_button("Cancel", use_container_width=True)
    
    if bill_submitted:
        if bill_name and bill_amount > 0:
            success = create_bill(household_info['household_id'], bill_name, bill_amount, bill_due_date)
            if success:
                st.success("Bill created successfully!")
                get_upcoming_bills.clear()
                st.session_state.show_create_bill_form = False
                st.rerun()
        else:
            st.warning("Please enter a valid name and amount.")
    
    if cancel_bill:
        st.session_state.show_create_bill_form = False
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# CATEGORY MANAGEMENT SECTION
# ============================================================

st.markdown('<h4 style="color: white;">Manage Categories</h4>', unsafe_allow_html=True)

categories_df = get_categories(household_info['household_id'])

# Display existing categories (only shared type)
with st.expander("📁 View All Categories", expanded=False):
    if not categories_df.empty:
        # Filter to only show shared categories
        shared_categories = categories_df[categories_df['type'] == 'shared']
        
        if not shared_categories.empty:
            st.markdown(f"<span style='color: black; font-weight: bold;'>Shared Categories</span>", unsafe_allow_html=True)
            for idx, row in shared_categories.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<span style='color: black;'>• {row['name']}</span>", unsafe_allow_html=True)
                with col2:
                    if is_admin():
                        if st.button("🗑️", key=f"delete_cat_{row['category_id']}", help="Delete category"):
                            if delete_category(row['category_id'], household_info['household_id']):
                                st.success(f"Deleted category: {row['name']}")
                                get_categories.clear()
                                st.rerun()
        else:
            st.info("No shared categories found for this household")
    else:
        st.info("No categories found for this household")

# Toggle button for creating new category (admin only)
if 'show_create_category_form' not in st.session_state:
    st.session_state.show_create_category_form = False

if is_admin():
    if st.button("➕ Create New Category", key="toggle_create_category"):
        st.session_state.show_create_category_form = not st.session_state.show_create_category_form

if st.session_state.show_create_category_form and is_admin():
    st.markdown("### Create a new shared category")
    
    with st.form("create_category_form"):
        category_name = st.text_input("Category Name", placeholder="e.g. Groceries, Transportation, Entertainment")
        st.caption("This category will be available for user-to-user payments and shared expenses")
        
        col_submit, col_cancel = st.columns(2)
        with col_submit:
            category_submitted = st.form_submit_button("Create Category", use_container_width=True)
        with col_cancel:
            cancel_category = st.form_submit_button("Cancel", use_container_width=True)
    
    if category_submitted:
        if category_name:
            # Always create as 'shared' type
            success = create_category(household_info['household_id'], category_name, 'shared')
            if success:
                st.success(f"Shared category '{category_name}' created successfully!")
                get_categories.clear()
                st.session_state.show_create_category_form = False
                st.rerun()
        else:
            st.warning("Please enter a category name.")
    
    if cancel_category:
        st.session_state.show_create_category_form = False
        st.rerun()
