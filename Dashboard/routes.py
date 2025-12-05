"""
Routes and Business Logic for HomeBase Dashboard
This module contains higher-level functions and UI logic that use CRUD operations.
"""

import streamlit as st
import pandas as pd
from crud import (
    get_all_users, create_user, create_household, add_member_to_household,
    get_all_households, user_has_household, get_household_info,
    mark_bill_as_paid, delete_bill, get_upcoming_bills, create_category,
    delete_category, get_categories, pay_towards_goal, get_savings_goals,
    get_spending_data, get_recent_transactions, update_user_name
)


# ============================================================
# AUTHENTICATION & SESSION HELPERS
# ============================================================

def is_admin():
    """Check if current user has admin or co-admin privileges"""
    role = st.session_state.get('household_info', {}).get('role', 'member')
    return role in ['admin', 'co-admin']


def toggle_menu():
    """Toggle the menu visibility"""
    st.session_state.show_menu = not st.session_state.show_menu


def toggle_master_view():
    """Toggle master view mode"""
    st.session_state.show_master_view = not st.session_state.show_master_view


# ============================================================
# ONBOARDING
# ============================================================

def onboarding_screen():
    """Display onboarding screen for new users"""
    st.title("🏡 Welcome to Homebase")
    st.write("Let's get your account set up!")

    st.markdown("### 👤 Step 1 — Create your profile")
    username = st.text_input("Your name")
    email = st.text_input("Your email")

    st.markdown("### 🏠 Step 2 — Choose how to join Homebase")
    choice = st.radio(
        "Select an option:",
        ["Create a new household", "Join an existing household"]
    )

    selected_household = None
    if choice == "Join an existing household":
        households = get_all_households()
        if households.empty:
            st.info("No households exist yet. You must create one.")
            choice = "Create a new household"
        else:
            mapping = dict(zip(households["name"], households["household_id"]))
            selected_name = st.selectbox("Select a household", mapping.keys())
            selected_household = mapping[selected_name]

    if st.button("Continue"):
        if not username or not email:
            st.error("Enter both name and email.")
            return

        # Create new user
        new_user_id = create_user(username, email)
        if not new_user_id:
            return

        # Create or join household
        if choice == "Create a new household":
            household_name = f"{username}'s Household"
            new_house_id = create_household(household_name, new_user_id)
            add_member_to_household(new_house_id, new_user_id, role="admin")

            st.session_state.household_info = {
                "household_id": new_house_id,
                "name": household_name,
                "role": "admin"
            }

        else:
            add_member_to_household(selected_household, new_user_id, role="member")

            from crud import get_database_connection
            df = pd.read_sql(
                "SELECT name FROM Households WHERE household_id = %s",
                get_database_connection(),
                params=(selected_household,)
            )

            st.session_state.household_info = {
                "household_id": selected_household,
                "name": df.iloc[0]["name"],
                "role": "member"
            }

        # Save user info
        st.session_state.user_id = new_user_id
        st.session_state.user_info = {
            "username": username,
            "email": email,
            "user_id": new_user_id
        }

        st.success("Setup complete! Loading your dashboard…")
        st.rerun()


# ============================================================
# BILL MANAGEMENT
# ============================================================

@st.dialog("Add New Bill")
def show_add_bill_form(household_id):
    """Display form to create a new bill"""
    from crud import create_bill
    
    with st.form("bill_creation_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Bill Name", placeholder="e.g. Internet, Rent")
        with col2:
            amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
            
        due_date = st.date_input("Due Date")
        
        submitted = st.form_submit_button("Create Bill", use_container_width=True)
        
        if submitted:
            if name and amount > 0:
                success = create_bill(household_id, name, amount, due_date)
                if success:
                    get_upcoming_bills.clear()
                    st.success("Bill created successfully!")
                    st.rerun()
            else:
                st.warning("Please enter a valid name and amount.")


@st.dialog("Manage Bill")
def open_bill_action(bill_id, bill_name, amount):
    """Display bill management dialog"""
    st.write(f"**{bill_name}**")
    st.write(f"Amount: ${amount:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mark as Paid", use_container_width=True, type="primary"):
            success = mark_bill_as_paid(bill_id, st.session_state.user_id)
            if success:
                st.success("Bill paid")
                get_upcoming_bills.clear()
                get_recent_transactions.clear()
                st.rerun()

    with col2:
        if is_admin():
            if st.button("Delete Bill", use_container_width=True, type="secondary"):
                st.session_state[f"confirm_delete_{bill_id}"] = True

            if st.session_state.get(f"confirm_delete_{bill_id}", False):
                st.warning("Are you sure?")
                if st.button("Yes, Delete Permanently", type="primary", use_container_width=True):
                    success = delete_bill(bill_id)
                    if success:
                        st.success("Bill deleted.")
                        get_upcoming_bills.clear() 
                        st.rerun()
        else:
            st.caption("Admin only")


# ============================================================
# USER PROFILE MANAGEMENT
# ============================================================

def handle_user_profile_update(new_username):
    """Handle updating user profile information"""
    user_id_to_update = st.session_state.get('user_id')
    if not user_id_to_update:
        st.error("Error: User ID not found in session state.")
        return False
    
    if update_user_name(user_id_to_update, new_username):
        # Update session state with new username
        st.session_state.user_info['username'] = new_username
        get_spending_data.clear()
        return True
    return False


# ============================================================
# MASTER VIEW (ADMIN FEATURES)
# ============================================================

def render_master_view_selector():
    """Render master view user selector in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👥 Switch User View")

    # Select admin/non-admin
    user_type = st.sidebar.radio(
        "Select User Type",
        options=['admin', 'non-admin'],
        index=0,
        key="user_type_selector"
    )

    st.sidebar.caption(f"Select a {user_type} user to view their dashboard")

    # Load users
    all_users = get_all_users(user_type)

    if not all_users.empty:
        # Build dropdown options
        user_options = {row['username']: row['user_id'] for _, row in all_users.iterrows()}

        selected_user_label = st.sidebar.selectbox(
            "Select User",
            options=list(user_options.keys()),
            key="user_selector"
        )

        selected_user = selected_user_label

        # Load selected user context into session
        if selected_user:
            from crud import get_database_connection
            conn = get_database_connection()
            if conn:
                # Load user info
                df_user = pd.read_sql(
                    "SELECT user_id, username, email FROM Users WHERE username = %s",
                    conn,
                    params=(selected_user,)
                )

                if not df_user.empty:
                    st.session_state.user_id = int(df_user.iloc[0]["user_id"])
                    st.session_state.user_info = {
                        "user_id": int(df_user.iloc[0]["user_id"]),
                        "username": df_user.iloc[0]["username"],
                        "email": df_user.iloc[0]["email"]
                    }

                    # Load household info
                    df_hh = pd.read_sql(
                        """
                        SELECT h.household_id, h.name, hm.role
                        FROM HouseholdMembers hm
                        JOIN Households h ON hm.household_id = h.household_id
                        WHERE hm.user_id = %s
                        """,
                        conn,
                        params=(st.session_state.user_id,)
                    )

                    if not df_hh.empty:
                        st.session_state.household_info = {
                            "household_id": int(df_hh.iloc[0]["household_id"]),
                            "name": df_hh.iloc[0]["name"],
                            "role": df_hh.iloc[0]["role"]
                        }
                    else:
                        st.session_state.household_info = None

                st.sidebar.markdown("---")
                st.sidebar.info(f"Currently viewing: **{selected_user_label}** ({user_type})")

    else:
        st.sidebar.warning(f"No {user_type} users found in database")


# ============================================================
# CATEGORY MANAGEMENT UI
# ============================================================

def render_category_management(household_id):
    """Render category management section"""
    st.markdown('<h4 style="color: white;">Manage Categories</h4>', unsafe_allow_html=True)

    categories_df = get_categories(household_id)

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
                                if delete_category(row['category_id'], household_id):
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
                success = create_category(household_id, category_name, 'shared')
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


# ============================================================
# BILL MANAGEMENT UI
# ============================================================

def render_bill_management(household_id):
    """Render bill management section"""
    from crud import check_and_update_overdue_bills
    
    # Check and update overdue bills
    check_and_update_overdue_bills(household_id)
    
    # Initialize session state for create bill form
    if 'show_create_bill_form' not in st.session_state:
        st.session_state.show_create_bill_form = False

    if is_admin():
        if st.button("➕ Create New Bill", key="toggle_create_bill"):
            st.session_state.show_create_bill_form = not st.session_state.show_create_bill_form

    if st.session_state.show_create_bill_form and is_admin():
        st.markdown("### Create a new bill")
        
        from crud import create_bill
        
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
                success = create_bill(household_id, bill_name, bill_amount, bill_due_date)
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
