-- ============================================================
--  CREATE SCHEMA
-- ============================================================
CREATE DATABASE IF NOT EXISTS Homebase;
USE Homebase;

-- ============================================================
--  CREATE TABLES
-- ============================================================

-- USERS
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- HOUSEHOLDS
CREATE TABLE Households (
    household_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (admin_user_id) REFERENCES Users(user_id)
);

-- HOUSEHOLD MEMBERS
CREATE TABLE HouseholdMembers (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('admin','co-admin','member') NOT NULL,
    FOREIGN KEY (household_id) REFERENCES Households(household_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- CATEGORIES
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('bill','goal','shared') NOT NULL,
    FOREIGN KEY (household_id) REFERENCES Households(household_id)
);

-- TRANSACTIONS
CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    notes VARCHAR(255),
    is_shared BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES Households(household_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- SAVINGS GOALS
CREATE TABLE SavingsGoals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES Households(household_id)
);

-- BILLS
CREATE TABLE Bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE,
    status ENUM('pending','paid','overdue') DEFAULT 'pending',
    FOREIGN KEY (household_id) REFERENCES Households(household_id)
);

-- DEBT SETTLEMENTS
CREATE TABLE DebtSettlements (
    settlement_id INT AUTO_INCREMENT PRIMARY KEY,
    household_id INT NOT NULL,
    payer_user_id INT NOT NULL,
    receiver_user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending','settled','overdue') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES Households(household_id),
    FOREIGN KEY (payer_user_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_user_id) REFERENCES Users(user_id)
);

-- ============================================================
--  INSERT MOCK DATA
-- ============================================================

-- USERS
INSERT INTO Users (username, email) VALUES
('emma_perez','emma.perez@sororityu.edu'),
('natalie_cho','natalie.cho@sororityu.edu'),
('kayla_jones','kayla.jones@sororityu.edu'),
('isabella_fernandez','isabella.fernandez@sororityu.edu'),
('olivia_nguyen','olivia.nguyen@sororityu.edu'),
('mia_thompson','mia.thompson@sororityu.edu'),
('zoe_ali','zoe.ali@sororityu.edu'),
('harper_kim','harper.kim@sororityu.edu'),
('julia_davis','julia.davis@sororityu.edu'),
('ava_williams','ava.williams@sororityu.edu'),
('sophia_martinez','sophia.martinez@sororityu.edu'),
('madison_clark','madison.clark@sororityu.edu'),
('brooklyn_liu','brooklyn.liu@sororityu.edu'),
('bella_singh','bella.singh@sororityu.edu'),
('lucy_sanders','lucy.sanders@sororityu.edu'),
('riley_tanaka','riley.tanaka@sororityu.edu'),
('chloe_richards','chloe.richards@sororityu.edu'),
('elena_garcia','elena.garcia@sororityu.edu'),
('hailey_owens','hailey.owens@sororityu.edu'),
('megan_white','megan.white@sororityu.edu'),
('morgan_chen','morgan.chen@sororityu.edu'),
('sarah_yoon','sarah.yoon@sororityu.edu'),
('anna_keller','anna.keller@sororityu.edu'),
('ella_reed','ella.reed@sororityu.edu'),
('grace_hall','grace.hall@sororityu.edu'),
('madelyn_brown','madelyn.brown@sororityu.edu'),
('aubrey_cole','aubrey.cole@sororityu.edu'),
('nora_ellis','nora.ellis@sororityu.edu'),
('addison_price','addison.price@sororityu.edu'),
('leah_moore','leah.moore@sororityu.edu'),
('alex_rodriguez','alex.rodriguez@campusapt.com'),
('jamie_wong','jamie.wong@campusapt.com'),
('dylan_smith','dylan.smith@campusapt.com'),
('kai_patel','kai.patel@campusapt.com'),
('maria_gomez','maria.gomez@familyhome.com'),
('ricardo_gomez','ricardo.gomez@familyhome.com'),
('sofia_gomez','sofia.gomez@familyhome.com'),
('lucas_gomez','lucas.gomez@familyhome.com'),
('diego_gomez','diego.gomez@familyhome.com'),
('amelia_rivers','amelia.rivers@artcoop.org'),
('noah_clark','noah.clark@artcoop.org'),
('tariq_abdullah','tariq.abdullah@artcoop.org'),
('leila_fernandez','leila.fernandez@artcoop.org'),
('hannah_gold','hannah.gold@artcoop.org'),
('pastor_johnson','pastor.johnson@faithplace.org'),
('deacon_sam','deacon.sam@faithplace.org'),
('choir_amy','choir.amy@faithplace.org'),
('usher_michael','usher.michael@faithplace.org'),
('donor_rachel','donor.rachel@faithplace.org'),
('jade_mitchell','jade.mitchell@lovehome.com'),
('taylor_flores','taylor.flores@lovehome.com'),
('nana_ruth','nana.ruth@generationhome.com'),
('grandpa_al','grandpa.al@generationhome.com'),
('mom_ayesha','mom.ayesha@generationhome.com'),
('dad_malik','dad.malik@generationhome.com'),
('teen_jordan','teen.jordan@generationhome.com'),
('teen_maya','teen.maya@generationhome.com'),
('child_sam','child.sam@generationhome.com'),
('child_lina','child.lina@generationhome.com'),
('ethan_liu','ethan.liu@startupcafe.com'),
('naomi_baker','naomi.baker@startupcafe.com'),
('omar_khalid','omar.khalid@startupcafe.com'),
('emma_ross','emma.ross@startupcafe.com'),
('logan_park','logan.park@startupcafe.com');

-- HOUSEHOLDS
INSERT INTO Households (admin_user_id, name) VALUES
(1, 'Alpha Theta Sorority House'),
(31, 'Campus Corner Apartment'),
(35, 'Gomez Family Home'),
(40, 'Downtown Art Co-Op'),
(45, 'FaithPlace Community Church'),
(50, 'Jade & Taylor Love Nest'),
(52, 'The Johnson Generational Home'),
(60, 'Sunrise Café Founders');

-- HOUSEHOLD MEMBERS
-- (Insert household members for all 8 groups)
INSERT INTO HouseholdMembers (household_id, user_id, role) VALUES
-- Sorority House
(1, 1,'admin'),(1,2,'co-admin'),(1,3,'member'),(1,4,'member'),(1,5,'member'),(1,6,'member'),(1,7,'member'),(1,8,'member'),(1,9,'member'),
(1,10,'member'),(1,11,'member'),(1,12,'member'),(1,13,'member'),(1,14,'member'),(1,15,'member'),(1,16,'member'),(1,17,'member'),(1,18,'member'),
(1,19,'member'),(1,20,'member'),(1,21,'member'),(1,22,'member'),(1,23,'member'),(1,24,'member'),(1,25,'member'),(1,26,'member'),(1,27,'member'),
(1,28,'member'),(1,29,'member'),(1,30,'member'),

-- Apartment
(2,31,'member'),(2,32,'member'),(2,33,'member'),(2,34,'member'),

-- Family
(3,35,'admin'),(3,36,'co-admin'),(3,37,'member'),(3,38,'member'),(3,39,'member'),

-- Art Co-Op
(4,40,'admin'),(4,41,'co-admin'),(4,42,'member'),(4,43,'member'),(4,44,'member'),

-- Church
(5,45,'admin'),(5,46,'co-admin'),(5,47,'member'),(5,48,'member'),(5,49,'member'),

-- Couple
(6,50,'admin'),(6,51,'co-admin'),

-- Generational Household
(7,52,'admin'),(7,53,'co-admin'),(7,54,'member'),(7,55,'member'),(7,56,'member'),(7,57,'member'),(7,58,'member'),(7,59,'member'),

-- Entrepreneur Café
(8,60,'admin'),(8,61,'co-admin'),(8,62,'member'),(8,63,'member'),(8,64,'member');

-- ============================================================
-- CATEGORIES (see previous data)
-- ============================================================
INSERT INTO Categories (household_id, name, type) VALUES
-- Sorority
(1, 'Rent','bill'),(1,'Utilities','bill'),(1,'Events','goal'),(1,'Groceries','shared'),(1,'Repairs','bill'),
-- Apartment
(2,'Rent','bill'),(2,'Utilities','bill'),(2,'Streaming Subscriptions','shared'),(2,'Groceries','shared'),
-- Family
(3,'Groceries','shared'),(3,'Utilities','bill'),(3,'Vacation','goal'),(3,'School Supplies','shared'),
-- Art Co-Op
(4,'Art Supplies','shared'),(4,'Gallery Rent','bill'),(4,'Community Events','goal'),(4,'Marketing','shared'),
-- Church
(5,'Donations','goal'),(5,'Maintenance','bill'),(5,'Outreach','goal'),
-- Lesbian Couple
(6,'Groceries','shared'),(6,'Rent','bill'),(6,'Furniture','goal'),
-- Generational Household
(7,'Utilities','bill'),(7,'Groceries','shared'),(7,'Home Repairs','bill'),(7,'Education Fund','goal'),
-- Entrepreneur Café
(8,'Business Equipment','goal'),(8,'Lease Payment','bill'),(8,'Marketing','shared'),(8,'Supplies','shared');

-- ============================================================
-- TRANSACTIONS 
-- ============================================================
INSERT INTO Transactions (household_id, user_id, category_id, amount, notes, is_shared, created_at) VALUES
(1, 1, 1, 2500, 'Paid monthly rent', TRUE, NOW()),
(1, 2, 2, 300, 'Electric and water bills', TRUE, NOW()),
(1, 3, 3, 150, 'Event decoration budget', TRUE, NOW()),
(1, 5, 4, 120, 'Groceries for kitchen', TRUE, NOW()),
(1, 7, 3, 200, 'Formal event venue deposit', TRUE, NOW()),
(1, 10, 5, 75, 'Leaky pipe repair', TRUE, NOW()),
(1, 15, 4, 80, 'Snacks for study group', TRUE, NOW()),
-- Additional transactions for emma_perez (user_id = 1)
(1, 1, 4, 95, 'Weekly grocery run', TRUE, NOW()),
(1, 1, 2, 85, 'Internet bill contribution', TRUE, NOW()),
(1, 1, 3, 175, 'Bought decorations for winter formal', TRUE, NOW()),
(1, 1, 4, 65, 'Breakfast supplies for house', TRUE, NOW()),
(1, 1, 5, 120, 'Fixed broken washing machine', TRUE, NOW()),
-- Recent transactions for emma_perez - last week
(1, 1, 4, 45.50, 'Dinner at Applebees with sisters', TRUE, '2025-11-30 18:30:00'),
(1, 1, 4, 78.20, 'Grocery shopping at Trader Joes', TRUE, '2025-11-28 14:15:00'),
-- Recent transactions for emma_perez - last month
(1, 1, 4, 52.30, 'Lunch at Applebees', TRUE, '2025-11-20 12:45:00'),
(1, 1, 4, 92.15, 'Weekly groceries - Whole Foods', TRUE, '2025-11-14 16:20:00'),
(1, 1, 4, 38.75, 'Late night Applebees run', TRUE, '2025-11-07 21:30:00'),
-- Additional transactions from other Alpha Theta members
(1, 4, 4, 110, 'Grocery shopping trip', TRUE, NOW()),
(1, 6, 3, 50, 'Contributed to event fund', TRUE, NOW()),
(1, 8, 4, 75, 'Kitchen supplies and snacks', TRUE, NOW()),
(1, 11, 2, 40, 'Utilities contribution', TRUE, NOW()),
(1, 12, 4, 90, 'Food for house dinner', TRUE, NOW()),
(1, 14, 3, 125, 'Formal event ticket purchases', TRUE, NOW()),
(1, 16, 5, 60, 'Repair fund contribution', TRUE, NOW()),
(1, 18, 4, 85, 'Groceries for communal fridge', TRUE, NOW()),
(1, 20, 2, 55, 'Split utility payment', TRUE, NOW()),
(1, 25, 3, 80, 'Sisterhood retreat deposit', TRUE, NOW()),
-- Recent Alpha Theta transactions (November - December 2) - Last 7 days
(1, 2, 4, 62.45, 'Pizza night for study group', TRUE, '2025-12-01 19:45:00'),
(1, 5, 4, 48.30, 'Coffee and bagels for house', TRUE, '2025-11-30 08:30:00'),
(1, 7, 3, 95.00, 'Holiday party decorations', TRUE, '2025-11-29 15:20:00'),
(1, 10, 4, 71.80, 'Grocery run - Costco', TRUE, '2025-11-27 13:10:00'),
-- Recent Alpha Theta transactions (November) - Earlier in month
(1, 3, 4, 55.25, 'House breakfast supplies', TRUE, '2025-11-24 10:15:00'),
(1, 9, 2, 45.00, 'Gas bill contribution', TRUE, '2025-11-22 16:30:00'),
(1, 13, 4, 83.50, 'Groceries and cleaning supplies', TRUE, '2025-11-19 14:45:00'),
(1, 15, 3, 120.00, 'Formal dress shopping trip', TRUE, '2025-11-17 12:00:00'),
(1, 17, 4, 39.90, 'Snacks for movie night', TRUE, '2025-11-15 18:20:00'),
(1, 19, 4, 67.75, 'Weekly grocery shopping', TRUE, '2025-11-12 11:30:00'),
(1, 22, 5, 85.00, 'Fixed kitchen sink', TRUE, '2025-11-10 09:45:00'),
(1, 24, 4, 54.20, 'Dinner ingredients for house', TRUE, '2025-11-08 17:00:00'),
(1, 26, 3, 75.00, 'Philanthropy event supplies', TRUE, '2025-11-05 13:25:00'),
(1, 28, 4, 42.60, 'Late night Taco Bell run', TRUE, '2025-11-03 22:15:00'),
-- Apartment
(2,31,6,450,'Rent payment - October',TRUE,NOW()),
(2,32,6,450,'Rent share',TRUE,NOW()),
(2,33,7,60,'Wi-Fi and utilities split',TRUE,NOW()),
(2,34,8,90,'Groceries for the week',TRUE,NOW()),
(2,32,9,15,'Netflix shared sub',TRUE,NOW()),
-- Family
(3,35,10,180,'Grocery trip',TRUE,NOW()),
(3,36,11,250,'Gas and electricity bill',TRUE,NOW()),
(3,37,12,100,'Vacation savings contribution',TRUE,NOW()),
(3,38,13,45,'New school supplies',FALSE,NOW()),
(3,39,10,25,'Snacks for lunch',FALSE,NOW()),
-- Art Co-Op
(4,40,14,350,'Paint and brushes bulk order',TRUE,NOW()),
(4,41,15,2000,'Paid gallery lease',TRUE,NOW()),
(4,42,16,100,'Community event poster print',TRUE,NOW()),
(4,43,17,120,'Promoted art show on social media',TRUE,NOW()),
-- Church
(5,45,18,300,'October tithes collected',TRUE,NOW()),
(5,46,19,150,'Building maintenance',TRUE,NOW()),
(5,47,20,80,'Homeless shelter donation drive',TRUE,NOW()),
(5,49,18,50,'Personal donation',FALSE,NOW()),
-- Lesbian Couple
(6,50,21,120,'Weekly groceries',TRUE,NOW()),
(6,51,22,950,'Rent payment',TRUE,NOW()),
(6,50,23,200,'Purchased new couch',TRUE,NOW()),
-- Generational Household
(7,52,24,300,'Electric + water bills',TRUE,NOW()),
(7,53,25,250,'Grocery shopping',TRUE,NOW()),
(7,54,26,500,'Roof repair deposit',TRUE,NOW()),
(7,55,27,200,'Education fund for children',TRUE,NOW()),
(7,57,25,40,'Snacks and milk',FALSE,NOW()),
-- Entrepreneur Café
(8,60,28,2500,'Espresso machine down payment',TRUE,NOW()),
(8,61,29,1200,'Lease payment for store',TRUE,NOW()),
(8,62,30,300,'Instagram ad campaign',TRUE,NOW()),
(8,63,31,450,'Purchased beans and cups',TRUE,NOW()),
(8,64,30,200,'Boosted local launch post',TRUE,NOW());

-- ============================================================
-- SAVINGS GOALS
-- ============================================================
INSERT INTO SavingsGoals (household_id, name, target_amount, current_amount, created_at) VALUES
(1,'Spring Break Trip to Miami',6000,1800,NOW()),
(1,'Greek Life Formal Event',2500,700,NOW()),
(2,'New Gaming PC Setup',2000,400,NOW()),
(2,'Spring Break Cabin Rental',1200,600,NOW()),
(3,'Family Vacation to Disney',5000,2500,NOW()),
(3,'Emergency Savings Fund',10000,3500,NOW()),
(4,'Community Mural Project',4000,2200,NOW()),
(4,'Gallery Lighting Upgrade',1500,500,NOW()),
(5,'Charity Drive Fund',8000,6500,NOW()),
(5,'Youth Outreach Program',3000,900,NOW()),
(6,'Moving Fund',2500,1800,NOW()),
(6,'Adoption & Legal Fees',10000,2500,NOW()),
(7,'Home Renovation Project',12000,6000,NOW()),
(7,'College Fund for Grandkids',20000,8000,NOW()),
(8,'Cafe Espresso Machine',7000,3500,NOW()),
(8,'Storefront Rent Deposit',9000,5000,NOW());

-- ============================================================
-- BILLS
-- ============================================================
INSERT INTO Bills (household_id, name, amount, due_date, status) VALUES
(1,'Internet Bill',120,'2025-10-20','pending'),
(1,'Water & Utilities',340,'2025-10-25','paid'),
(1,'House Cleaning Service',250,'2025-12-15','pending'),
(1,'Security System Subscription',95,'2025-12-28','pending'),
(2,'Electric Bill',90,'2025-10-15','overdue'),
(2,'WiFi Subscription',60,'2025-10-18','pending'),
(3,'Mortgage Payment',2000,'2025-11-01','pending'),
(3,'Car Insurance',300,'2025-10-22','paid'),
(4,'Studio Rent',850,'2025-10-25','pending'),
(4,'Website Hosting',120,'2025-10-17','paid'),
(5,'Utility Bill',500,'2025-10-21','pending'),
(5,'Building Maintenance',1200,'2025-10-28','pending'),
(6,'Apartment Rent',1450,'2025-11-01','pending'),
(6,'Streaming Services',25,'2025-10-14','paid'),
(7,'Property Tax',3500,'2025-12-01','pending'),
(7,'Family Car Loan',450,'2025-10-25','paid'),
(8,'Shop Utilities',600,'2025-10-20','pending'),
(8,'Supplier Invoice',1250,'2025-10-22','overdue');

-- ============================================================
-- DEBT SETTLEMENTS
-- ============================================================
INSERT INTO DebtSettlements (household_id, payer_user_id, receiver_user_id, amount, status, created_at) VALUES
(1,5,1,45,'pending',NOW()),
(1,9,2,30,'settled',NOW()),
(2,15,16,25,'settled',NOW()),
(2,17,18,40,'pending',NOW()),
(3,22,20,60,'pending',NOW()),
(4,26,24,150,'settled',NOW()),
(5,31,29,100,'pending',NOW()),
(6,34,35,80,'settled',NOW()),
(7,38,36,70,'pending',NOW()),
(8,43,40,500,'pending',NOW());

-- ---------------------

-- show household 8 content in debtsettlements

use homebase;
SELECT * 
FROM debtsettlements
WHERE household_id = 8;

-- UPDATE to pending to settled 

UPDATE debtsettlements
SET status = 'settled'
WHERE household_id = 8 AND payer_user_id = 43 AND receiver_user_id = 40;

SELECT * 
FROM debtsettlements
WHERE household_id = 8;


-- DELETE 

DELETE FROM debtsettlements 
WHERE household_id = 8 AND payer_user_id = 43 AND receiver_user_id = 40;


SELECT * 
FROM debtsettlements
WHERE household_id = 8;
-- -------------------------------

-- Create an index to speed up lookups by email
CREATE INDEX idx_users_email ON Users(email);

SHOW INDEX FROM Users;

SELECT * FROM Users WHERE email = 'emma.perez@sororityu.edu';


-- Add a "reminder_date" column to the Bills table
ALTER TABLE Bills
ADD COLUMN reminder_date DATE AFTER due_date;

SELECT * 
FROM Bills;

-- Remove the "reminder_date" column from the Bills table
ALTER TABLE Bills
DROP COLUMN reminder_date;

SELECT * 
FROM Bills;

-- -----------------------------

-- INNER JOIN 
-- Lists all users who are members of households, showing which household they belong to and their role.
SELECT u.username, h.name AS household_name, hm.role
FROM HouseholdMembers hm
JOIN Users u ON hm.user_id = u.user_id
JOIN Households h ON hm.household_id = h.household_id;


-- LEFT OUTER JOIN 
-- this query retrieves all households, whether or not they have any associated bills.
SELECT h.name AS household_name, b.name AS bill_name, b.status
FROM Households h
LEFT JOIN Bills b ON h.household_id = b.household_id;

-- Aggregate SUM of how much is spent in each Cateogry, by What User, IN household_ID = 1
SELECT 
    h.name AS household_name,
    u.username AS user_name,
    c.name AS category_name,
    SUM(t.amount) AS total_spent
FROM Transactions t
JOIN Users u ON t.user_id = u.user_id
JOIN Categories c ON t.category_id = c.category_id
JOIN Households h ON t.household_id = h.household_id
WHERE t.household_id = 1
GROUP BY h.name, u.username, c.name
ORDER BY c.name, total_spent DESC;



-- Get users who are admins of any household
use homebase;
SELECT username
FROM Users
WHERE user_id IN (
    SELECT admin_user_id
    FROM Households
);

-- Creating a view of all admins from this subquery

CREATE VIEW AdminUsers AS
SELECT username, user_id
FROM Users
WHERE user_id IN (
    SELECT admin_user_id
    FROM Households
);

SELECT * FROM AdminUsers;

-- Creating a view of all non-admin users

CREATE VIEW NonAdminUsers AS
SELECT username, user_id
FROM Users
WHERE user_id NOT IN (
    SELECT admin_user_id
    FROM Households
);

SELECT * FROM NonAdminUsers;





