pred_query = '''WITH customer AS( 
    SELECT c.customer_id, c.customer_active_end_date,c.erp_crm_application_id, c.customer_active_start_date 
    FROM rwanda_kenya.customer c WHERE c.ngu='Rwanda'),

payments AS(
    SELECT p.customer_id,(p.payment_utc_timestamp) AS payment_date,p.amount FROM rwanda_kenya.payment p),

customer_info AS(
    SELECT customer_id, customer_birth_date FROM rwanda_kenya.customer_personal_details),

daily_snapshot AS(
    SELECT dcs.customer_id, DATE(dcs.date_timestamp) as date_timestamp, dcs.daily_rate, dcs.utilisation_rate, dcs.balance AS balance_left,
    dcs.bonus_no_cash_ontime_used, dcs.enable_ontime_used,dcs.bundle_ontime_used 
    FROM rwanda_kenya.daily_customer_snapshot dcs
),

payment_counts as(
        Select c.customer_id,
    count(p.payment_date) as total_payments_before_msg_date,AVG(p.amount)/AVG(ds.daily_rate) as payment_frequency
    FROM payments p
    INNER JOIN customer c
    ON c.customer_id=p.customer_id
    INNER JOIN daily_snapshot ds
    on ds.customer_id=c.customer_id and ds.date_timestamp=(SELECT CURRENT_DATE) - INTERVAL '1 DAYS'
    GROUP BY c.customer_id
    ),
msg as
(
Select distinct c.customer_id ,c.customer_active_start_date, c.customer_active_end_date,max(sq.msg_creation_date) over (partition by c.customer_id) as msg_creation_date,sq.target_id 

from rwanda_kenya.customer c 
inner join
src_erp_rwanda_kenya.smscentre_queue sq
on sq.target_id =c.erp_crm_application_id
where sq.campaign_id =54 and c.ngu='Rwanda'
)



    SELECT distinct
    m.customer_id,m.msg_creation_date, m.customer_active_start_date,pc.total_payments_before_msg_date,pc.payment_frequency, m.customer_active_end_date,
    ci.customer_birth_date,ds.daily_rate, ds.utilisation_rate,
    ds.balance_left, ds.bonus_no_cash_ontime_used, ds.enable_ontime_used, ds.bundle_ontime_used,
    min(p.payment_utc_timestamp) over (partition by m.customer_id) as pay_date 
    FROM  msg m
    inner join rwanda_kenya.payment p 
    on p.customer_id =m.customer_id and p.payment_utc_timestamp >m.msg_creation_date 
    INNER JOIN customer_info ci 
    ON ci.customer_id = m.customer_id
    INNER JOIN daily_snapshot ds 
    ON ds.customer_id =m.customer_id  AND DATE(ds.date_timestamp)=(SELECT CURRENT_DATE) - INTERVAL '1 DAYS' 
    INNER JOIN payment_counts pc
    on pc.customer_id=m.customer_id



'''