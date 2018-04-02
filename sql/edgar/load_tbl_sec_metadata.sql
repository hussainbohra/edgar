use edgar;

load data from s3 's3://data.daizika.com/sec/edgar/extract/metadata/temp/metadata.csv' 
into table tbl_sec_metadata
fields terminated by ',' enclosed by '"'
lines terminated by '\n'
ignore 1 lines
(dt_file,cik,name,sic,irs,stateofinc,business_street,business_city,business_state,business_zip,business_phone,mail_street,mail_city,mail_state,mail_zip);

create table tbl_sec_metadata_copy as
select a.*
from tbl_sec_metadata a
join (select cik, max(dt_file) max_dt_file from tbl_sec_metadata group by cik) b
on a.cik = b.cik
and a.dt_file = b.max_dt_file;

truncate table tbl_sec_metadata;

insert into tbl_sec_metadata(dt_file, cik, name,sic,irs, stateofinc, business_street, business_city, business_state, business_zip, business_phone, mail_street, mail_city, mail_state, mail_zip)
select distinct dt_file, cik, name,sic,irs, stateofinc, business_street, business_city, business_state, business_zip, business_phone, mail_street, mail_city, mail_state, mail_zip from tbl_sec_metadata_copy;

drop table tbl_sec_metadata_copy;

load data from s3 's3://data.daizika.com/sec/edgar/extract/metadata/temp/company_name_changes.csv' 
into table tbl_sec_namechanges
fields terminated by ',' enclosed by '"'
lines terminated by '\n'
ignore 1 lines
(dt_file,cik,name,dt_change);

create table tbl_sec_namechanges_copy as
select max(dt_file) dt_file, cik, dt_change, name  
from tbl_sec_namechanges 
group by cik, dt_change, name;

truncate table tbl_sec_namechanges;

insert into tbl_sec_namechanges(dt_file, cik, dt_change, name)
select dt_file, cik, dt_change, name from tbl_sec_namechanges_copy;

drop table tbl_sec_namechanges_copy;

