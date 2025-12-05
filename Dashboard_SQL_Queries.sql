

-- ============================================================
-- USER MANAGEMENT QUERIES
-- ============================================================

-- Get user information
SELECT username, email 
FROM Users 
WHERE user_id = %s;

-- Create new user
INSERT INTO Users (username, email) 
VALUES (%s, %s);

-- Update username
UPDATE Users 
SET username = %s 
WHERE user_id = %s;

-- Get user by username
SELECT user_id, username, email 
FROM Users 
WHERE username = %s;

-- Get users from admin view
SELECT user_id, username
FROM adminusers
ORDER BY user_id;

-- Get users from non-admin view
SELECT user_id, username
FROM nonadminusers
ORDER BY user_id;


-- ============================================
-- HOUSEHOLD MANAGEMENT QUERIES
-- ============================================

-- Get household information for user
SELECT h.household_id, h.name, hm.role
FROM Households h
JOIN HouseholdMembers hm ON h.household_id = hm.household_id
WHERE hm.user_id = %s
LIMIT 1;

-- Create new household
INSERT INTO Households (admin_user_id, name)
VALUES (%s, %s);

-- Get all households
SELECT household_id, name 
FROM Households 
ORDER BY name;

-- Get household name by ID
SELECT name 
FROM Households 
WHERE household_id = %s;

-- Get household members
SELECT u.user_id, u.username
FROM Users u
JOIN HouseholdMembers hm ON u.user_id = hm.user_id
WHERE hm.household_id = %s
ORDER BY u.username;

-- Add member to household
INSERT INTO HouseholdMembers (household_id, user_id, role)
VALUES (%s, %s, %s);

-- Check if user has household
SELECT household_id, role
FROM HouseholdMembers
WHERE user_id = %s
LIMIT 1;


-- =================================
-- TRANSACTION QUERIES
-- =================================

-- Get recent transactions
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
LIMIT 10;

-- Insert transaction record
INSERT INTO Transactions (household_id, user_id, category_id, amount, notes, is_shared)
VALUES (%s, %s, %s, %s, %s, TRUE);


-- ============================================================
-- SPENDING ANALYTICS QUERIES
-- ============================================================

-- Total household spending by category
-- Extracts specific names from Bill and Contribution transactions
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
GROUP BY category;

-- Average spending per user
SELECT 
    u.username,
    AVG(t.amount) AS avg_amount
FROM Transactions t
JOIN Users u ON t.user_id = u.user_id
WHERE t.household_id = %s 
AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
GROUP BY u.username
ORDER BY avg_amount DESC
LIMIT 5;

-- User vs household spending comparison
SELECT 
    SUM(CASE WHEN t.user_id = %s THEN t.amount ELSE 0 END) AS my_spending,
    SUM(CASE WHEN t.user_id != %s THEN t.amount ELSE 0 END) AS household_spending
FROM Transactions t
WHERE t.household_id = %s 
AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY);

-- User's total spending by category
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
GROUP BY category;

-- User's average spending by category
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
ORDER BY avg_amount DESC;

-- Cumulative spending over time
SELECT 
    DATE(t.created_at) AS date,
    SUM(t.amount) AS daily_total
FROM Transactions t
WHERE t.household_id = %s 
AND t.user_id = %s
AND t.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
GROUP BY DATE(t.created_at)
ORDER BY date ASC;


-- ============================================================
-- CATEGORY MANAGEMENT QUERIES
-- ============================================================

-- Get all categories for household
SELECT category_id, name, type
FROM Categories
WHERE household_id = %s
ORDER BY type, name;

-- Create new category
INSERT INTO Categories (household_id, name, type)
VALUES (%s, %s, %s);

-- Delete category
DELETE FROM Categories 
WHERE category_id = %s AND household_id = %s;

-- Check if category exists
SELECT category_id 
FROM Categories 
WHERE household_id = %s AND name = %s AND type = %s;


-- ============================================================
-- BILL MANAGEMENT QUERIES
-- ============================================================

-- Get upcoming bills
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
LIMIT 10;

-- Create new bill
INSERT INTO Bills (household_id, name, amount, due_date, status)
VALUES (%s, %s, %s, %s, 'pending');

-- Update overdue bills
UPDATE Bills 
SET status = 'overdue' 
WHERE household_id = %s 
AND status = 'pending' 
AND due_date < CURRENT_DATE;

-- Get bill details
SELECT household_id, name, amount 
FROM Bills 
WHERE bill_id = %s;

-- Mark bill as paid
UPDATE Bills 
SET status = 'paid' 
WHERE bill_id = %s;

-- Delete bill
DELETE FROM Bills 
WHERE bill_id = %s;


-- ============================================================
-- SAVINGS GOALS QUERIES
-- ============================================================

-- Get all savings goals for household
SELECT 
    goal_id,
    name,
    target_amount,
    current_amount,
    created_at
FROM SavingsGoals
WHERE household_id = %s
ORDER BY created_at DESC;

-- Get savings goal details
SELECT current_amount, target_amount, name 
FROM SavingsGoals 
WHERE goal_id = %s AND household_id = %s;

-- Update savings goal amount
UPDATE SavingsGoals 
SET current_amount = %s 
WHERE goal_id = %s AND household_id = %s;

-- Create new savings goal
INSERT INTO SavingsGoals (household_id, name, target_amount, current_amount)
VALUES (%s, %s, %s, %s);

-- Delete savings goal
DELETE FROM SavingsGoals 
WHERE goal_id = %s AND household_id = %s;


-- ============================================================
-- DEBT SETTLEMENT QUERIES
-- ============================================================

-- Get debt settlements for user
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
ORDER BY ds.created_at DESC;

-- Get receiver username for payment
SELECT username 
FROM Users 
WHERE user_id = %s;

-- Insert debt settlement record
INSERT INTO DebtSettlements (household_id, payer_user_id, receiver_user_id, amount, status)
VALUES (%s, %s, %s, %s, 'settled');


-- ============================================================
-- NOTES
-- ============================================================

/*
PARAMETER TYPES:
%s - Placeholder for parameterized queries (prevents SQL injection)

COMMON PARAMETERS:
- user_id: Integer user identifier
- household_id: Integer household identifier
- category_id: Integer category identifier
- bill_id: Integer bill identifier
- goal_id: Integer savings goal identifier
- amount: Float/Decimal monetary value
- days: Integer number of days for date calculations
- username: String username
- email: String email address
- name: String for household/category/bill/goal names
- due_date: Date value
- status: String status value ('pending', 'paid', 'overdue', 'settled')
- role: String role ('admin', 'co-admin', 'member')
- type: String category type ('shared', 'bill', 'goal')
