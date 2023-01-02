#!/usr/bin/env python
# coding: utf-8

# In[ ]:


payment_status='''select sq.msg_creation_date,c.customer_id,(dcs.date_timestamp) as payment_status_date,dcs.payment_status  from src_erp_rwanda_kenya.smscentre_queue sq 
inner join 
rwanda_kenya.customer c 
on c.erp_crm_application_id =sq.target_id 
inner join 
rwanda_kenya.customer_personal_details cpd 
on c.customer_id =cpd.customer_id 
inner join 
rwanda_kenya.daily_customer_snapshot dcs 
on
dcs.customer_id =c.customer_id and dcs.date_timestamp = date(sq.msg_creation_date+4)
where c.ngu='Rwanda' and sq.state !='e' and substring(sq.mobile,5)=substring(cpd.customer_phone_1,2)
and sq.campaign_id =54

order by sq.msg_creation_date desc;'''

