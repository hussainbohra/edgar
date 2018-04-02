use edgar;

load data from s3 's3://data.daizika.com/sec/edgar/index/full/form_2017_QTR1.csv' 
into table edgar.tbl_sec_fillings
fields terminated by ',' enclosed by '"'
lines terminated by '\n'
ignore 1 lines
(f_year,f_month,f_day,dt_file,form_id,company_name,cik,edgar_file,form_url,target_folder,target_file);

