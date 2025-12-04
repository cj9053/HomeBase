use homebase;

# after Emma Pays someone

SELECT *
FROM debtsettlements t
JOIN users u 
    ON t.payer_user_id = u.user_id
WHERE u.username = 'emma_perez';



# When savings goals change
SELECT *
FROM savingsgoals sg
JOIN households h
    ON sg.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';



# When bills change
SELECT *
FROM bills b
JOIN households h
    ON b.household_id = h.household_id
WHERE h.name = 'Alpha Theta Sorority House';

select *
from households;

select * 
from users
where username = 'jerry';

select * 
from householdmembers hm
join households h
	on h.household_id = hm.household_id
WHERE h.name = 'Alpha Theta Sorority House';
