
/* create table scaffold as
 select distinct patient_num,start_date from observation_fact
 order by patient_num,start_date;
*/

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
)
-- select * from dcat
select patient_num,start_date,vid,group_concat(datconcat,';') datconcat from dcat
-- where concept_cd in (select concept_cd from var where concept_path = '\i2b2\Procorders\Imaging\US ORDERABLES\') 
-- and modifier_cd = '@'
group by patient_num,start_date,vid;

/* 
next step: pivot on vid! Which is not supported in SQL, so get ready to write a bunch of 
self-joins and then parameterize
*/
