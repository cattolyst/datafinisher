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
