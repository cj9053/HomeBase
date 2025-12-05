"""
CRUD Operations for HomeBase Dashboard
This module contains all database operations and SQL queries.
"""

import streamlit as st
import mysql.connector
import pandas as pd
from decimal import Decimal


@st.cache_resource
def get_database_connection():
    """Establish connection to MySQL database using credentials from Streamlit secrets.toml."""
    try:
        creds = st.secrets.get("mysql", {})
        host = creds.get("host")
        port = int(creds.get("port")) if creds.get("port") else 3306
        user = creds.get("user")
        password = creds.get("password")
        database = creds.get("database")

        if not all([host, user, password, database]):
            st.error("Database credentials missing. Please set st.secrets['mysql'] with host, user, password, and database.")
            return None

        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


# ============================================================
# USER OPERATIONS
# ============================================================

@st.cache_data(ttl=300)
def get_user_info(user_id):
    """Get user information"""
    user_id = int(user_id)
    
    conn = get_database_connection()
    if conn:
        query = "SELECT username, email FROM Users WHERE user_id = %s"
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


def create_user(username, email):
    """Insert a new user into Users table."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Users (username, email) VALUES (%s, %s)"
            cursor.execute(query, (username, email))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            get_all_users.clear()
            return new_id
        except Exception as e:
            st.error(f"Error creating user: {e}")
    return None


def update_user_name(user_id, new_username):
    """Update user's username"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            user_id_int = int(user_id)
            query = "UPDATE Users SET username = %s WHERE user_id = %s" 
            cursor.execute(query, (new_username, user_id_int))
            conn.commit()
            cursor.close()
            get_user_info.clear()
            return True 
        except Exception as e:
            st.error(f"Error updating user: {e}")
            return False
    return False


# ============================================================
# HOUSEHOLD OPERATIONS
# ============================================================

@st.cache_data(ttl=300)
def get_household_info(user_id):
    """Get household information for user"""
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
def get_all_households():
    """Get all households available."""
    conn = get_database_connection()
    if conn:
        try:
            df = pd.read_sql(
                "SELECT household_id, name FROM Households ORDER BY name",
                conn
            )
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def create_household(household_name, admin_user_id):
    """Create a new household and assign admin_user_id."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO Households (admin_user_id, name)
                VALUES (%s, %s)
            """
            cursor.execute(query, (admin_user_id, household_name))
            conn.commit()
            new_household_id = cursor.lastrowid
            cursor.close()
            return new_household_id
        except Exception as e:
            st.error(f"Error creating household: {e}")
    return None


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


def add_member_to_household(household_id, user_id, role="member"):
    """Add a user to HouseholdMembers table."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO HouseholdMembers (household_id, user_id, role)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (household_id, user_id, role))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error adding member: {e}")
    return False


def user_has_household(user_id):
    """Return household_id and role if user belongs to a household, otherwise None."""
    conn = get_database_connection()
    if conn:
        try:
            df = pd.read_sql(
                """
                SELECT household_id, role
                FROM HouseholdMembers
                WHERE user_id = %s
                LIMIT 1
                """,
                conn,
                params=(user_id,)
            )
            if df.empty:
                return None
            return df.iloc[0].to_dict()
        except Exception as e:
            st.error(f"Error checking household: {e}")
    return None


# ============================================================
# BILL OPERATIONS
# ============================================================

@st.cache_data(ttl=300)
def get_upcoming_bills(household_id):
    """Get upcoming bills"""
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
            return True
        except Exception as e:
            st.error(f"Error creating bill: {e}")
            return False
    return False


def check_and_update_overdue_bills(household_id):
    """Update overdue bills status"""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
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
    """Mark a bill as paid and optionally create a transaction"""
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


def delete_bill(bill_id):
    """Delete a bill"""
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


# ============================================================
# TRANSACTION OPERATIONS
# ============================================================

@st.cache_data(ttl=60)
def get_recent_transactions(household_id, days=365):
    """Get recent transactions for a household"""
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
    household_id = int(household_id)
    user_id = int(user_id)
    period_days = int(period_days)
    
    conn = get_database_connection()
    if conn:
        # Total household spending by category
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


# ============================================================
# CATEGORY OPERATIONS
# ============================================================

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


# ============================================================
# DEBT SETTLEMENT OPERATIONS
# ============================================================

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


# ============================================================
# SAVINGS GOAL OPERATIONS
# ============================================================

@st.cache_data(ttl=300)
def get_savings_goals(household_id):
    """Get savings goals"""
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
