use edgar;

drop table if exists tbl_sec_fillings;

create table tbl_sec_fillings (
  id int auto_increment primary key
 ,f_year int
 ,f_month int
 ,f_day int
 ,dt_file datetime
 ,form_id nvarchar(20)
 ,company_name nvarchar(250)
 ,cik int
 ,edgar_file nvarchar(250)
 ,form_url nvarchar(1000)
 ,target_folder nvarchar(1000)
 ,target_file nvarchar(1000)
 );
 
create index idx_dt_file on tbl_sec_fillings (dt_file);
create index idx_cik on tbl_sec_fillings (cik);
create index idx_form_id on tbl_sec_fillings (form_id);
create index idx_company_name on tbl_sec_fillings (company_name);

