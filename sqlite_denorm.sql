
/* create table scaffold as
 select distinct patient_num,start_date from observation_fact
 order by patient_num,start_date;
*/

-- uncomment the below line in order to remove the table so you can create it again
-- drop table scaffold;

-- All unique combinations of patients and dates, onto which to later join individual facts
-- don't try to create and populate with data in one step, because start_dates get turned into DATETIMES
CREATE TABLE
    scaffold
    (
        patient_num NUM,
        start_date DATE
    );

-- uncomment the below line and run it in order to empty out the table for a fresh round of inserts
-- delete from scaffold;
insert into scaffold (patient_num, start_date) 
select distinct patient_num, date(start_date) start_date
from observation_fact order by patient_num, start_date;



-- this maps concept_path to all its contained concept_cds and their data domains
-- select distinct vr.*,concept_cd,substr(concept_cd,1,instr(concept_cd,':')) ddomain 
-- from variable vr join concept_dimension cd on cd.concept_path like vr.concept_path||'%';

with recursive 
var(concept_path,concept_cd,ddomain,vid) as (
select distinct vr.concept_path,concept_cd,substr(concept_cd,1,instr(concept_cd,':')) ddomain, id
from variable vr join concept_dimension cd on cd.concept_path like vr.concept_path||'%'
where concept_cd not like 'DEM|AGEATV:%'
),
dcat(patient_num,start_date,concept_cd,vid,datconcat) as (select distinct patient_num,start_date,observation_fact.concept_cd
,vid,observation_fact.concept_cd||' & '||ifnull(modifier_cd,'')||' & '||ifnull(valtype_cd,'')||' & '||ifnull(tval_char,'')
||' & '||ifnull(nval_num,'')||' & '||lower(ifnull(units_cd,''))
||' & '||ifnull(instance_num,'')||' & '||encounter_num
-- might need to do left join? dropping stuff that's not in the variable table?
from observation_fact join var on var.concept_cd = observation_fact.concept_cd
order by patient_num,start_date,encounter_num,observation_fact.concept_cd,modifier_cd,valtype_cd,tval_char,lower(units_cd)
), 

dcat2(pn, st, vid, datconcat) as
-- select * from dcat
(select patient_num pn,start_date st,vid,group_concat(datconcat,';') datconcat from dcat
-- where concept_cd in (select concept_cd from var where concept_path = '\i2b2\Procorders\Imaging\US ORDERABLES\') 
-- and modifier_cd = '@'
group by patient_num,start_date,vid),

vid05(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 5),
vid06(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 6),
vid07(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 7),
vid09(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 9),
vid12(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 12),
vid44(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 44)

/* we will not be using these, these are the two sexes coded in a really backwards way
vid36(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 36),
vid42(pn, st, datconcat) as (select pn, st, datconcat from dcat2 where vid = 42)
*/ 

select patient_num, start_date
,vid05.datconcat v05,vid06.datconcat v06,vid07.datconcat v07,vid09.datconcat v09,vid12.datconcat v12, vid44.datconcat v44
/*vid36.datconcat vid36, vid42.datconcat vid42 */
from scaffold 
left join vid05 on vid05.pn = patient_num and vid05.st = start_date
left join vid06 on vid06.pn = patient_num and vid06.st = start_date
left join vid07 on vid07.pn = patient_num and vid07.st = start_date
left join vid09 on vid09.pn = patient_num and vid09.st = start_date
left join vid12 on vid12.pn = patient_num and vid12.st = start_date
left join vid44 on vid44.pn = patient_num and vid44.st = start_date
;
/*
left join vid36 on vid36.pn = patient_num and vid36.st = start_date
left join vid42 on vid42.pn = patient_num and vid42.st = start_date
*/

/* which variables are not available in a more convenient form from patient_dimension? The below query tells you*/
-- select * from variable where name not like '%old at visit' and name not in ('Male','Female','Living');

--next step: generate a script that searches the variable table and dynamically adds as many rows and new table names, etc. as needed.

