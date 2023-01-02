#!/usr/bin/env python
# coding: utf-8

# In[ ]:


msg_df = '''
WITH customer AS( 
    SELECT c.customer_id, c.erp_crm_application_id, c.customer_active_end_date, c.customer_active_start_date 
    FROM rwanda_kenya.customer c WHERE c.ngu='Rwanda'),

sms AS(
    SELECT sq.target_id ,sq.campaign_id, sq.state,sq.mobile, sq.msg_creation_date,
    COALESCE(lead(sq.msg_creation_date ,1) over(partition by sq.target_id order by sq.msg_creation_date ASC),(SELECT CURRENT_DATE)) as nxt_msg_date
    FROM src_erp_rwanda_kenya.smscentre_queue sq 
    WHERE sq.target_record LIKE 'bboxx.crm.application%' AND sq.campaign_id =54 AND sq.msg_creation_date >='2022-01-01' AND sq.state!='e'),

payments AS(
    SELECT p.customer_id,(p.payment_utc_timestamp) AS payment_date,p.amount FROM rwanda_kenya.payment p where p.ngu='Rwanda'),

customer_info AS(
    SELECT customer_id, customer_birth_date, customer_phone_1 FROM rwanda_kenya.customer_personal_details),

daily_snapshot AS(
    SELECT dcs.customer_id, DATE(dcs.date_timestamp) as date_timestamp, dcs.daily_rate, dcs.utilisation_rate, dcs.balance AS balance_left,
    dcs.bonus_no_cash_ontime_used, dcs.enable_ontime_used,dcs.bundle_ontime_used,AVG(dcs.daily_rate) over(PARTITION BY dcs.customer_id) as avg_daily_rate
    FROM rwanda_kenya.daily_customer_snapshot dcs),

temp as(
    SELECT c.customer_id, c.customer_active_start_date, c.customer_active_end_date, 
    s.mobile, s.msg_creation_date, s.nxt_msg_date, p.payment_date, p.amount,
    RANK() over (partition by c.customer_id, s.msg_creation_date order by p.payment_date asc) as pay_rank 
            FROM customer c 
            JOIN sms s on c.erp_crm_application_id = s.target_id
            JOIN payments p ON p.customer_id = c.customer_id AND p.payment_date BETWEEN s.msg_creation_date AND s.nxt_msg_date
            order by 1,s.msg_creation_date, payment_date asc),

temp2 as(
        Select p.customer_id,t.customer_active_start_date, t.customer_active_end_date,t.mobile, t.msg_creation_date, t.nxt_msg_date, 
        t.payment_date as after_msg_pay_date, t.amount,t.pay_rank,
    count(p.payment_date)OVER(partition by p.customer_id, t.msg_creation_date)as total_payments_before_msg_date,
    AVG(p.amount) over(PARTITION BY p.customer_id,t.msg_creation_date) as avg_amount
    From temp t
    INNER JOIN payments p
    on p.customer_id=t.customer_id  
    where t.pay_rank=1 AND t.msg_creation_date>p.payment_date
        )

    SELECT distinct
    t.customer_id,t.total_payments_before_msg_date,(t.avg_amount/ds.daily_rate) as payment_frequency, t.customer_active_start_date,
    t.customer_active_end_date, t.msg_creation_date, t.nxt_msg_date, t.amount,
    ci.customer_birth_date,t.after_msg_pay_date,ds.daily_rate, ds.utilisation_rate, ds.balance_left, ds.bonus_no_cash_ontime_used, 
    ds.enable_ontime_used, ds.bundle_ontime_used 
    FROM temp2 t
    INNER JOIN customer_info ci 
    ON ci.customer_id = t.customer_id AND SUBSTRING(t.mobile,5)= SUBSTRING(ci.customer_phone_1,2)
    INNER JOIN daily_snapshot ds 
    ON ds.customer_id =t.customer_id  AND DATE(ds.date_timestamp)=DATE(t.msg_creation_date)

    WHERE pay_rank = 1 


'''
