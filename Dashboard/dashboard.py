from streamlit_extras.stylable_container import stylable_container as sc
import streamlit as st

import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from decimal import Decimal


# Styling for the page
 
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
def get_all_users(user_type='admin'):
    """Get users from the specified view (admin or non-admin)"""
    conn = get_database_connection()
    if conn:
        if user_type == 'non-admin':
            view_name = 'nonadminusers'
        else:
            view_name = 'adminusers'
        
        query = f"""
            SELECT user_id, username
            FROM {view_name}
            ORDER BY user_id
        """
        df = pd.read_sql(query, conn)
        return df
    return pd.DataFrame()

#check and uddate  Bill start CJ
def check_and_update_overdue_bills(household_id):
  
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # SQL to bulk update any bill that is pending and past today
            query = """
                UPDATE Bills 
                SET status = 'overdue' 
                WHERE household_id = %s 
                AND status = 'pending' 
                AND due_date < CURRENT_DATE
            """

            cursor.execute(query, (int(household_id),))
            conn.commit()
            cursor.close()

        except Exception as e:
            st.error(f"Error updating overdue bills: {e}")


def mark_bill_as_paid(bill_id, user_id=None):

    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get bill details
            cursor.execute("SELECT household_id, name, amount FROM Bills WHERE bill_id = %s", (bill_id,))
            bill_result = cursor.fetchone()
            
            if bill_result:
                household_id = bill_result[0]
                bill_name = bill_result[1]
                bill_amount = bill_result[2]
                
                # Update bill status
                query = "UPDATE Bills SET status = 'paid' WHERE bill_id = %s"
                cursor.execute(query, (bill_id,))
                
                # Create transaction if user_id is provided
                if user_id is not None:
                    # Get or create permanent 'Bill' category
                    category_id = get_or_create_permanent_category(household_id, 'Bill', 'bill')
                    
                    if category_id:
                        transaction_query = """
                            INSERT INTO Transactions (household_id, user_id, category_id, amount, notes, is_shared)
                            VALUES (%s, %s, %s, %s, %s, TRUE)
                        """
                        transaction_notes = f"Paid bill: {bill_name}"
                        cursor.execute(transaction_query, (household_id, user_id, category_id, float(bill_amount), transaction_notes))
                
                conn.commit()
                cursor.close()
                return True
        except Exception as e:
            st.error(f"Error updating bill: {e}")
            return False
    return False




@st.dialog("Manage Bill")
def open_bill_action(bill_id, bill_name, amount):

    st.write(f"**{bill_name}**")
    st.write(f"Amount: ${amount:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:

        if st.button("Mark as Paid", use_container_width=True, type="primary"):
            success = mark_bill_as_paid(bill_id, st.session_state.user_id)
            if success:
                st.success("Bill paid")
                get_upcoming_bills.clear() # Clear cache so it vanishes from list
                st.rerun()


    with col2:
        if is_admin():
            if st.button("Delete Bill", use_container_width=True, type="secondary"):
                st.session_state[f"confirm_delete_{bill_id}"] = True


            if st.session_state.get(f"confirm_delete_{bill_id}", False):
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


def delete_bill(bill_id):
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Bills WHERE bill_id = %s"
            cursor.execute(query, (bill_id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error deleting bill: {e}")
            return False
    return False

#check and update bill stats End CJ



@st.cache_data(ttl=60)
def get_recent_transactions(household_id, days=365):


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
        # For Bill and Contribution, extract the specific name from notes
        total_query = """
            SELECT 
                CASE 
                    WHEN c.name = 'Bill' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, ': ', -1), '\n', 1)
                    WHEN c.name = 'Contribution' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, 'to ', -1), '\n', 1)
                    ELSE c.name
                END AS category,
                SUM(t.amount) AS total
            FROM Transactions t
            JOIN Categories c ON t.category_id = c.category_id
            WHERE t.household_id = %s 
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY category
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

@st.cache_data(ttl=60)
def get_user_spending_data(household_id, user_id, period_days):
    """Get individual user spending data for 'My spending' view"""
    household_id = int(household_id)
    user_id = int(user_id)
    period_days = int(period_days)
    
    conn = get_database_connection()
    if conn:
        # User's total spending by category
        # For Bill and Contribution, extract the specific name from notes
        user_category_query = """
            SELECT 
                CASE 
                    WHEN c.name = 'Bill' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, ': ', -1), '\n', 1)
                    WHEN c.name = 'Contribution' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, 'to ', -1), '\n', 1)
                    ELSE c.name
                END AS category,
                SUM(t.amount) AS total
            FROM Transactions t
            JOIN Categories c ON t.category_id = c.category_id
            WHERE t.household_id = %s 
            AND t.user_id = %s
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY category
        """
        user_category_df = pd.read_sql(user_category_query, conn, params=(household_id, user_id, period_days))
        
        # User's average spending by category
        user_avg_category_query = """
            SELECT 
                CASE 
                    WHEN c.name = 'Bill' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, ': ', -1), '\n', 1)
                    WHEN c.name = 'Contribution' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(t.notes, 'to ', -1), '\n', 1)
                    ELSE c.name
                END AS category,
                AVG(t.amount) AS avg_amount
            FROM Transactions t
            JOIN Categories c ON t.category_id = c.category_id
            WHERE t.household_id = %s 
            AND t.user_id = %s
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY category
            ORDER BY avg_amount DESC
        """
        user_avg_category_df = pd.read_sql(user_avg_category_query, conn, params=(household_id, user_id, period_days))
        
        # Cumulative spending over time
        cumulative_query = """
            SELECT 
                DATE(t.created_at) AS date,
                SUM(t.amount) AS daily_total
            FROM Transactions t
            WHERE t.household_id = %s 
            AND t.user_id = %s
            AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(t.created_at)
            ORDER BY date ASC
        """
        cumulative_df = pd.read_sql(cumulative_query, conn, params=(household_id, user_id, period_days))
        
        # Calculate cumulative sum
        if not cumulative_df.empty:
            cumulative_df['cumulative_total'] = cumulative_df['daily_total'].cumsum()
        
        return user_category_df, user_avg_category_df, cumulative_df
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def get_household_members(household_id):
    """Get all members of a household"""
    household_id = int(household_id)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT u.user_id, u.username
            FROM Users u
            JOIN HouseholdMembers hm ON u.user_id = hm.user_id
            WHERE hm.household_id = %s
            ORDER BY u.username
        """
        df = pd.read_sql(query, conn, params=(household_id,))
        return df
    return pd.DataFrame()

def record_payment_to_user(household_id, payer_user_id, receiver_user_id, amount, category_id):
    """Record a payment/debt settlement between household members"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get receiver username for transaction notes
            cursor.execute("SELECT username FROM Users WHERE user_id = %s", (int(receiver_user_id),))
            receiver_result = cursor.fetchone()
            receiver_name = receiver_result[0] if receiver_result else "User"
            
            # Insert debt settlement record
            query = """
                INSERT INTO DebtSettlements (household_id, payer_user_id, receiver_user_id, amount, status)
                VALUES (%s, %s, %s, %s, 'settled')
            """
            cursor.execute(query, (int(household_id), int(payer_user_id), int(receiver_user_id), float(amount)))
            
            # Insert transaction record
            transaction_query = """
                INSERT INTO Transactions (household_id, user_id, category_id, amount, notes, is_shared)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """
            transaction_notes = f"Payment to {receiver_name}"
            cursor.execute(transaction_query, (int(household_id), int(payer_user_id), int(category_id), float(amount), transaction_notes))
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error recording payment: {e}")
            return False
    return False

def get_or_create_permanent_category(household_id, category_name, category_type):
    """Get or create a permanent category (Bill or Contribution)"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if category exists
            cursor.execute("""
                SELECT category_id FROM Categories 
                WHERE household_id = %s AND name = %s AND type = %s
            """, (int(household_id), category_name, category_type))
            result = cursor.fetchone()
            
            if result:
                category_id = result[0]
            else:
                # Create the permanent category
                cursor.execute("""
                    INSERT INTO Categories (household_id, name, type)
                    VALUES (%s, %s, %s)
                """, (int(household_id), category_name, category_type))
                conn.commit()
                category_id = cursor.lastrowid
            
            cursor.close()
            return category_id
        except Exception as e:
            st.error(f"Error getting/creating category: {e}")
            return None
    return None

@st.cache_data(ttl=60)
def get_categories(household_id):
    """Get all categories for a household"""
    household_id = int(household_id)
    conn = get_database_connection()
    if conn:
        query = """
            SELECT category_id, name, type
            FROM Categories
            WHERE household_id = %s
            ORDER BY type, name
        """
        df = pd.read_sql(query, conn, params=(household_id,))
        return df
    return pd.DataFrame()

def create_category(household_id, name, category_type):
    """Create a new category for a household"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO Categories (household_id, name, type)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (int(household_id), name, category_type))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error creating category: {e}")
            return False
    return False

def delete_category(category_id, household_id):
    """Delete a category from a household"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Categories WHERE category_id = %s AND household_id = %s"
            cursor.execute(query, (int(category_id), int(household_id)))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error deleting category: {e}")
            return False
    return False

@st.cache_data(ttl=60)
def get_user_debt_settlements(household_id, user_id):
    """Get debt settlements where user is payer or receiver"""
    household_id = int(household_id)
    user_id = int(user_id)
    
    conn = get_database_connection()
    if conn:
        query = """
            SELECT 
                ds.settlement_id,
                ds.amount,
                ds.status,
                ds.created_at,
                payer.username AS payer_name,
                receiver.username AS receiver_name,
                ds.payer_user_id,
                ds.receiver_user_id
            FROM DebtSettlements ds
            JOIN Users payer ON ds.payer_user_id = payer.user_id
            JOIN Users receiver ON ds.receiver_user_id = receiver.user_id
            WHERE ds.household_id = %s 
            AND (ds.payer_user_id = %s OR ds.receiver_user_id = %s)
            ORDER BY ds.created_at DESC
        """
        df = pd.read_sql(query, conn, params=(household_id, user_id, user_id))
        return df
    return pd.DataFrame()

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

## added a delete option (Snaha)
def delete_savings_goal(goal_id, household_id):
    """Delete a savings goal"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM SavingsGoals WHERE goal_id = %s AND household_id = %s"
            cursor.execute(query, (int(goal_id), int(household_id)))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error deleting savings goal: {e}")
            return False
    return False

def pay_towards_goal(goal_id, household_id, payment_amount, user_id=None):
    """Add payment towards a savings goal, ensuring it doesn't exceed target"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # First get current and target amounts, and goal name
            select_query = "SELECT current_amount, target_amount, name FROM SavingsGoals WHERE goal_id = %s AND household_id = %s"
            cursor.execute(select_query, (int(goal_id), int(household_id)))
            result = cursor.fetchone()
            
            if result:
                current_amount = float(result[0])
                target_amount = float(result[1])
                goal_name = result[2]
                new_amount = current_amount + float(payment_amount)
                
                # Check if payment would exceed target
                if new_amount > target_amount:
                    cursor.close()
                    return False, "Payment would exceed target amount"
                
                # Update the current amount
                update_query = "UPDATE SavingsGoals SET current_amount = %s WHERE goal_id = %s AND household_id = %s"
                cursor.execute(update_query, (new_amount, int(goal_id), int(household_id)))
                
                # If user_id is provided, create a transaction record
                if user_id is not None:
                    # Get or create permanent 'Contribution' category
                    category_id = get_or_create_permanent_category(int(household_id), 'Contribution', 'goal')
                    
                    if category_id:
                        # Insert transaction record
                        transaction_query = """
                            INSERT INTO Transactions (household_id, user_id, category_id, amount, notes, is_shared)
                            VALUES (%s, %s, %s, %s, %s, TRUE)
                        """
                        transaction_notes = f"Contribution to {goal_name}"
                        cursor.execute(transaction_query, (int(household_id), int(user_id), category_id, float(payment_amount), transaction_notes))
                
                conn.commit()
                cursor.close()
                return True, "Payment added successfully"
            else:
                cursor.close()
                return False, "Goal not found"
        except Exception as e:
            return False, f"Error updating savings goal: {e}"
    return False, "Database connection failed"


def update_user_name(new_username):
    user_id_to_update = st.session_state.get('user_id') # Use .get for safety
    if not user_id_to_update:
        st.error("Error: User ID not found in session state.")
        print("Error: User ID not found in session state.")
        return False
        
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            user_id_int = int(user_id_to_update)
            query = "UPDATE Users SET username = %s WHERE user_id = %s" 
            cursor.execute(query, (new_username, user_id_int))
            conn.commit()
            cursor.close()
            
            # Update the session state here, so the new username persists 
            # and is available on the next run.
            st.session_state.user_info['username'] = new_username
            

            get_user_info.clear()
            get_spending_data.clear()
            return True 
        except Exception as e:
            st.error(f"Error updating user: {e}")
            print(f"Error updating user: {e}")
            return False
    return False



# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1  # Default user for demo
if 'user_info' not in st.session_state:
    user_info = get_user_info(st.session_state.user_id)
    st.session_state.user_info = {
        'username': user_info['username'], 
        'email': user_info['email'],
        'user_id': st.session_state.user_id
    }
if 'household_info' not in st.session_state:
    household_data = get_household_info(st.session_state.user_id)
    
    if household_data is not None:
        st.session_state.household_info = {
            'household_id': household_data['household_id'], 
            'name': household_data['name'],
            # 🔥 CRUCIAL FIX: Ensure the 'role' is included here
            'role': household_data['role'] 
        }
    else:
        # Handle case where household data is not found
        st.session_state.household_info = {'role': 'N/A', 'name': 'N/A', 'household_id': None}
if 'show_menu' not in st.session_state:
    st.session_state.show_menu = False
if 'show_master_view' not in st.session_state:
    st.session_state.show_master_view = False
if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False

user_info = st.session_state.get('user_info', None) 
household_info = st.session_state.get('household_info', None)

# Helper function to check admin privileges
def is_admin():
    """Check if current user has admin or co-admin privileges"""
    role = st.session_state.get('household_info', {}).get('role', 'member')
    return role in ['admin', 'co-admin']

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
    
    # User type selection
    user_type = st.sidebar.radio(
        "Select User Type",
        options=['admin', 'non-admin'],
        index=0,
        key="user_type_selector"
    )
    
    st.sidebar.caption(f"Select a {user_type} user to view their dashboard")
    
    # Get users based on selected type
    all_users = get_all_users(user_type)
    
    if not all_users.empty:
        # Create user selection dropdown
        user_options = {}
        for idx, row in all_users.iterrows():
            label = f"{row['username']}"
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
            # Clear user and household info to force reload
            if 'user_info' in st.session_state:
                del st.session_state.user_info
            if 'household_info' in st.session_state:
                del st.session_state.household_info
            st.cache_data.clear()
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.info(f"Currently viewing: **{selected_user_label}** ({user_type})")
    else:
        st.sidebar.warning(f"No {user_type} users found in database")
else:
    st.session_state.show_master_view = False

# Get user and household data

# household_info = get_household_info(st.session_state.user_id)
household_info = st.session_state.get('household_info', {})

if user_info is None or household_info is None:
    st.error("Unable to load user or household information. Please check your database connection.")
    st.stop()

# Header Section
col_header_left, col_header_right = st.columns([9, 3])

with col_header_left:

    st.markdown(f'<p class="welcome-text">Welcome back, {user_info["username"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="homebase-name">{household_info["name"]}</h1>', unsafe_allow_html=True)

# UI create bill CJ
@st.dialog("Add New Bill")
def show_add_bill_form(household_id):
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
                    st.rerun() # Refresh app to show new bill in dashboard
            else:
                st.warning("Please enter a valid name and amount.")


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
    
                st.markdown("""
                    <h3 class="account-header-container">Account Details</h3>
                """, unsafe_allow_html=True)

            with col2:
               
                if st.button("Edit", key="edit_account_btn"):
                    # Put the code that handles editing here
                    st.session_state.show_edit_form = True # Example of using session state

           
            st.write(f"Username: {current_user_info.get('username', 'N/A')}")
            st.write(f"Email: {current_user_info.get('email', 'N/A')}")
            st.write(f"Role: {current_household_info.get('role', 'N/A')}")
            st.markdown("---")
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

            if st.session_state.show_edit_form:
                st.markdown("<br>", unsafe_allow_html=True) # Add spacing
                st.subheader("📝 Edit User Information")

            # Use st.form to group inputs and handle submission cleanly
                with st.form("edit_user_form", clear_on_submit=False):
                
                # Username Input
                    new_username = st.text_input(
                        "New Username", 
                        value=current_user_info['username'], # Pre-fill with current value
                    )
                    
                    # Password Input (Masked)
                    new_password = st.text_input(
                        "New Password", 
                        type="password", # Important for hiding input
                    )
                    
                    # Save and Cancel Buttons
                    col_save, col_cancel = st.columns(2)
                
                    with col_save:
                        save_submitted = st.form_submit_button("Save Changes")
                    if save_submitted:
                        print('save submit click')
                        username_changed = new_username != st.session_state.user_info['username']
                        if username_changed:
                            if update_user_name(new_username):
                                st.success(f"Username successfully updated to **{new_username}**.")
                                print((f"Username successfully updated to **{new_username}**."))
                            else:
                                st.error("Failed to update username in the database.")
                    
                    # 2. Update Password Logic
                        password_changed = bool(new_password)
                        if password_changed:
                            # **Call your backend/DB function to hash and update password here**
                            st.success("Password successfully updated.")
                        
                    # 3. Hide the form and Rerun if any changes occurred
                        if username_changed or password_changed:
                            st.session_state.show_edit_form = False
                            st.rerun() # Essential to reflect changes and hide form
                        
                    # with col_cancel:
                    #     cancel_btn = st.button("Cancel", key="cancel_edit_btn")
                    #     if cancel_btn:

                    #         st.session_state.show_edit_form = False
                    #         st.rerun() # Rerun to immediately hide the form
                cancel_btn = st.button("Cancel", key="cancel_edit_btn_outside")
                if cancel_btn:
                    st.session_state.show_edit_form = False
                    st.rerun() # Rerun to immediately hide the form
        
                        
            

st.markdown("<br>", unsafe_allow_html=True)

# create Bill Func CJ
def create_bill(household_id, name, amount, due_date):
    """Insert a new bill into the database"""
    household_id = int(household_id)  
    amount = float(amount)            
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO Bills (household_id, name, amount, due_date, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """
            cursor.execute(query, (household_id, name, amount, due_date))
            conn.commit()
            cursor.close()
            # conn.close()
            return True
        except Exception as e:
            st.error(f"Error creating bill: {e}")
            return False
    return False

  
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
 # spending toggle feature Snaha begins
    view_mode = st.radio(
        "Spending view",
        options=["My spending", "Household spending"],
        index=1,
        horizontal=True,
        label_visibility="collapsed"
    )
    # spending toggle feature Snaha ends


# Map period to days
period_days_map = {
    "Week": 7,
    "Month": 30,
    "Quarter": 90,
    "Year": 365
}
period_days = period_days_map[period]

# Get spending data based on view mode
if view_mode == "My spending":
    user_category_df, user_avg_category_df, cumulative_df = get_user_spending_data(
        household_info['household_id'], 
        st.session_state.user_id, 
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
    # Household spending view (original charts)
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

# Pay a Household Member Section
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

# Recent Transactions - Full Width
st.markdown('<h4 style="color: white;">Recent Transactions</h4>', unsafe_allow_html=True)
# Increase days to 365 to get more historical transactions
transactions_df = get_recent_transactions(household_info['household_id'], days=365)
with st.expander("Recent Transactions", expanded=False,):
    if not transactions_df.empty:
        for index, row in transactions_df.iterrows():
            # Build your HTML string using f-strings
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

#create savings goals feature Snaha begins

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
                    pay_clicked = False  # No payment option for achieved goals
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
                    
                    # Check if payment amount exceeds remaining
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
                            st.session_state[f"show_payment_dialog_{goal_id}"] = False
                            st.rerun()
                        else:
                            st.error(message)
                            # Don't close the dialog - just show the error
                            # User can adjust the amount and try again
                    
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
else:
    st.info("Only admins and co-admins can create new savings goals")

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

# create saving goals feature Snaha ends

st.markdown("<br>", unsafe_allow_html=True)

# Upcoming Bills Section
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
else:
    st.info("Only admins and co-admins can create new bills")

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

# Category Management Section
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
else:
    st.info("Only admins and co-admins can create new categories")

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


