use edgar;

drop table if exists tbl_sec_metadata;

create table tbl_sec_metadata (
  id int auto_increment primary key
 ,dt_file datetime
 ,cik int
 ,name nvarchar(250)
 ,sic nvarchar(250)
 ,irs nvarchar(250)
 ,stateofinc nvarchar(250)
 ,business_street nvarchar(250)
 ,business_city nvarchar(250)
 ,business_state nvarchar(2)
 ,business_zip nvarchar(250)
 ,business_phone nvarchar(250)
 ,mail_street nvarchar(250)
 ,mail_city nvarchar(250)
 ,mail_state nvarchar(2)
 ,mail_zip nvarchar(250)
 );
 
create index idx_dt_file on tbl_sec_metadata (dt_file);
create index idx_cik on tbl_sec_metadata (cik);
create index idx_name on tbl_sec_metadata (name);
create index idx_sic on tbl_sec_metadata (sic);

drop table if exists tbl_sec_namechanges;

create table tbl_sec_namechanges (
  id int auto_increment primary key
 ,dt_file datetime
 ,cik int
 ,name nvarchar(250)
 ,dt_change datetime
 );
 
create index idx_dt_file on tbl_sec_namechanges (dt_file);
create index idx_dt_change on tbl_sec_namechanges (dt_change);
create index idx_cik on tbl_sec_namechanges (cik);
create index idx_name on tbl_sec_namechanges (name);
