use homebase;

# When users are updated
SELECT *
FROM users u;


# When households are added 
SELECT *
FROM households h;

# ---------------------------------------

# When savings goals change in Alpha Theta
SELECT *
FROM savingsgoals sg
JOIN households h
    ON sg.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';


# When bills change in Alpha Theta
SELECT *
FROM bills b
JOIN households h
    ON b.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';


# when categories are updated in Alpha Theta
SELECT *
FROM categories c
JOIN households h
    ON c.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';

# --------------------------------------------------

# When household members are changed in Alpha Theta
SELECT *
FROM householdmembers hm
JOIN households h
    ON hm.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';


# When user-to-user payment change in Alpha Theta
SELECT *
FROM debtsettlements t
JOIN households h
    ON t.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';


# When Transactions are updated Alpha Theta
SELECT *
FROM transactions t
JOIN households h
    ON t.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';


