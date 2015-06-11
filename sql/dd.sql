create table if not exists data_dictionary as 
select cdid.*,mxinsts,mxfacts,'v'||substr('000'||cid,-3,3) colid,concept_path,name,mod,tval_char,nval_num,valueflag_cd,units_cd,confidence_num,quantity_num,location_cd,valtype_cd,0 done
from (select id cid,group_concat(distinct ddomain) ddomain,count(distinct ccd) ccd from cdid group by id) cdid
left join variable on cid = variable.id
left join (
select count(distinct modifier_cd) mod,id from obs_all
join cdid on concept_cd = ccd
where modifier_cd is not null 
and modifier_cd != '@'
group by id) mdid on cid = mdid.id
left join (
select count(distinct tval_char) tval_char,id from obs_all
join cdid on concept_cd = ccd
where tval_char is not null and tval_char not in ('E','TNP')
group by id) tvid on cid = tvid.id
left join (
select distinct 1 nval_num,id from obs_all
join cdid on concept_cd = ccd
where nval_num is not null
order by id) nvid on cid = nvid.id
left join (
select count(distinct valueflag_cd) valueflag_cd,id from obs_all
join cdid on concept_cd = ccd
where valueflag_cd is not null 
group by id) vfid on cid = vfid.id
left join (
select count(distinct units_cd) units_cd,id from obs_all
join cdid on concept_cd = ccd
where units_cd is not null
group by id) unid on cid = unid.id
left join (
select count(distinct confidence_num) confidence_num,id from obs_all
join cdid on concept_cd = ccd
where confidence_num is not null
group by id) cnid on cid = cnid.id
left join (
select count(distinct quantity_num) quantity_num,id from obs_all
join cdid on concept_cd = ccd
where quantity_num is not null
group by id) qnid on cid = qnid.id
left join (
select count(distinct location_cd) location_cd,id from obs_all
join cdid on concept_cd = ccd
where location_cd is not null
group by id) loid on cid = loid.id
left join (
select group_concat(distinct valtype_cd) valtype_cd,id from obs_all
join cdid on concept_cd = ccd
where valtype_cd is not null
group by id) vtid on cid = vtid.id
left join (
select id,max(cnt) mxinsts from (
        select id,patient_num,start_date,count(*) cnt
        from obs_all join cdid on ccd = concept_cd
        group by patient_num,start_date,id
) group by id) counts on cid = counts.id
left join (
select id,max(cnt) mxfacts from (
        select id,patient_num,start_date,count(*) cnt
        from obs_noins join cdid on ccd = concept_cd
        group by patient_num,start_date,id
) group by id) fcounts on cid = fcounts.id
