with recursive 
var(concept_path,concept_cd,ddomain,vid) as (
select distinct vr.concept_path,concept_cd,substr(concept_cd,1,instr(concept_cd,':')) ddomain, id
from variable vr join concept_dimension cd on cd.concept_path like vr.concept_path||'%'
where concept_cd not like 'DEM|AGEATV:%' name not in ('Living','Female','Male')
),
dcat(patient_num,start_date,concept_cd,vid,datconcat) as (select distinct patient_num,start_date,observation_fact.concept_cd
,vid,observation_fact.concept_cd||' & '||ifnull(modifier_cd,'')||' & '||ifnull(valtype_cd,'')||' & '||ifnull(tval_char,'')
||' & '||ifnull(nval_num,'')||' & '||lower(ifnull(units_cd,''))
||' & '||ifnull(instance_num,'')||' & '||encounter_num
from observation_fact join var on var.concept_cd = observation_fact.concept_cd
order by patient_num,start_date,encounter_num,observation_fact.concept_cd,modifier_cd,valtype_cd,tval_char,lower(units_cd)
), 
dcat2(pn, st, vid, datconcat) as
(select patient_num pn,start_date st,vid,group_concat(datconcat,';') datconcat from dcat
group by patient_num,start_date,vid),

/* -- Query for dynamically generating SQL for pure code-only, no-mods tables
-- Notice we wrap start_date in date()... otherwise we have date-times which LOOK like they match but don't, causing join problems


select group_concat(colid) from data_dictionary dd
where coalesce(mod,dd.tval_char,dd.valueflag_cd,dd.units_cd,dd.confidence_num,dd.quantity_num,dd.location_cd,dd.valtype_cd,dd.nval_num,-1) = -1;
;

select ' left join (select patient_num,date(start_date) sd,replace(group_concat(distinct concept_cd),'','',''; '') '||colid||' from cdid join observation_fact ob on ccd = concept_cd where id = '||cid||' group by patient_num,date(start_date) order by patient_num,start_date) '||colid||' on '||colid||'.patient_num = scaffold.patient_num and '||colid||'.sd = scaffold.start_date'
from data_dictionary dd
where coalesce(mod,dd.tval_char,dd.valueflag_cd,dd.units_cd,dd.confidence_num,dd.quantity_num,dd.location_cd,dd.valtype_cd,dd.nval_num,-1) = -1
and done != 1
;

-- then we mark those as done
update data_dictionary 
set done = 1
where coalesce(mod,tval_char,valueflag_cd,units_cd,confidence_num,quantity_num,location_cd,valtype_cd,nval_num,-1) = -1
and done != 1
;

-- then we select the pure code-only with-mods tables...
select group_concat(colid) from data_dictionary dd
where coalesce(dd.tval_char,dd.valueflag_cd,dd.units_cd,dd.confidence_num,dd.quantity_num,dd.location_cd,dd.valtype_cd,dd.nval_num,-1) = -1
and mod is not null
and done != 1
;

select ' left join (select patient_num,date(start_date) sd,replace(group_concat(distinct concept_cd||''=''||modifier_cd),'','',''; '') '||colid||' from cdid join observation_fact ob on ccd = concept_cd where id = '||cid||' group by patient_num,date(start_date) order by patient_num,start_date) '||colid||' on '||colid||'.patient_num = scaffold.patient_num and '||colid||'.sd = scaffold.start_date'
from data_dictionary dd
where coalesce(dd.tval_char,dd.valueflag_cd,dd.units_cd,dd.confidence_num,dd.quantity_num,dd.location_cd,dd.valtype_cd,dd.nval_num,-1) = -1
and mod is not null
and done != 1
;

select * from data_dictionary 
where done != 1 and mod is not null 
and coalesce(tval_char,valueflag_cd,units_cd,confidence_num,quantity_num,location_cd,valtype_cd,nval_num,-1) = -1;

Next: 
* concepts w/o mods that have additional values but only once per patient-date combination
* concepts w/ mods that have additional values but only once per patient-date-mod combination
*/

