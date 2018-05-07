#COMP 543, Assignment #1
#Chengyin Liu, cl93

#Questions:

#1. Who has seen a flower at Alaska Flat?
select distinct s.person
from sightings s
where s.location = 'Alaska Flat'
order by s.person;
/*
person
----------
Donna
Helen
Jennifer
John
Maria
Michael
Robert
Sandra
*/

#2. Who has seen the same flower at both Moreland Mill and at Steve Spring?
select distinct s1.person
from sightings s1, sightings s2
where s1.person = s2.person
	and s1.name = s2.name
	and s1.location = 'Moreland Mill'
    and s2.location = 'Steve Spring'
order by s1.person;
/*
person
----------
Jennifer
*/

#3. What is the scientific name for each of the different flowers that have been sighted by either Michael or Robert above 8250 feet in elevation?
select distinct fl.comname, fl.genus, fl.species
from flowers fl, sightings s, features fe
where s.name = fl.comname and (s.person = 'Michael' or s.person = 'Robert')
    and fe.location = s.location and fe.elev > 8250
order by fl.comname, fl.genus, fl.species;
/*
comname, genus, species
----------
California flannelbush	Fremontodendron	californicum
Death camas	Zigadenus	venenosus
Douglas dustymaiden	Chaenactis	douglasii
Ithuriels spear	Triteleia	laxa
Leopard lily	Lilium	pardalinum
Oak violet	Viola	quercetorum
Sheltons violet	Viola	sheltonii
Showy Jacobs ladder	Polemonium	californicum
Varied-leaved jewelflower	Streptanthus	diversifolius
*/

#4. Which maps hold a location where someone has seen Alpine penstemon in August?
select distinct fe.map
from features fe, sightings s
where s.location = fe.location and s.name = 'Alpine penstemon' and date_format(s.sighted,'%m') = '08'
order by fe.map;
/*
map
----------
Claraville
Walker Pass
*/

#5. Which genus have more than one species recorded in the SSWC database?
select distinct fl1.genus
from flowers fl1, flowers fl2
where fl1.genus = fl2.genus and fl1.species != fl2.species
order by fl1.genus;
/*
genus
----------
Gilia
Mimulus
Penstemon
Viola
*/

#6. What is the common name of the most commonly sighted flower (in terms of number of sightings)?
drop view if exists sig;

create view sig as
select s.name, count(*) flower_count
from sightings s
group by s.name;

select s.name
from sightings s
group by s.name
having count(*) >= 
	(select max(sig.flower_count)
    from sig);

drop view if exists sig;
/*
name
----------
California flannelbush
*/

#7. Who has not seen a flower at a location of class Tower?
select distinct p.person
from people p
where p.person not in 
	(select s.person 
	from sightings s
		inner join features fe on fe.location = s.location
    where fe.class ='Tower')
order by p.person;
/*
person
----------
Brad
Donna
Helen
James
Jennifer
John
Pete
Robert
Sandra
Tim
*/

#8. For each feature class, compute the total number of flower sightings.
#Assumption: here "feature class" means the 'class' attribute in the feature table
select fe.class, count(*) sighting_number
from sightings s
	inner join features fe on fe.location = s.location
group by fe.class
order by fe.class;
/*
class, sighting_number
----------
Flat	40
Gap	20
Locale	103
Mine	50
Populated Place	6
Range	69
Ridge	5
Spring	17
Summit	114
Tower	2
*/

#9. For each month, compute the fraction of the various flower species that were observed. 
#For example, say that all of the sightings were in May and June. 
#If 56% of the different flowers were observed in May and 74% in June, your query should return {(May, .56), (June, .74)}. 
#Sort by month number (e.g. January, February, March, ...)
#Assumption: here "flower species" means different kinds of flowers with different common names
select date_format(s.sighted, '%M') month, count(distinct s.name)/sn.species_number species_fraction
from sightings s, 
	(select count(distinct fl.comname) species_number
	from flowers fl) sn
group by month, species_number
order by field(month, 'January', 'February', 'March', 'April', 'May', 'June', 
	'July', 'August', 'September', 'October', 'November', 'December');
/*
month, species_fraction
----------
April	0.2400
May	0.8000
June	0.8400
July	0.7200
August	0.5800
September	0.3600
*/

#10. Who has seen a flower on every summit on the Sawmill Mountain map, except for Cerro Noroeste?
drop view if exists loc;

create view loc as
select distinct fe.location
from features fe
where fe.class = 'Summit' and fe.map = 'Sawmill Mountain' and fe.location != 'Cerro Noroeste';

select s1.person
from sightings s1, loc l1
where s1.location = l1.location 
	and s1.person not in 
		(select s2.person
        from sightings s2
        where s2.location = 'Cerro Noroeste')
group by s1.person
having count(distinct s1.location) = 
	(select count(distinct l2.location)
    from loc l2);
    
drop view if exists loc;
/*
person
----------
Sandra
*/

#11. For those people who have seen all of the flowers in the SSWC database, what was the date at which they saw their last unseen flower? 
#In other words, at which date did they finish observing all of the flowers in the database?
drop view if exists sig;

create view sig as
select s.person, s.name, min(s.sighted) date
from sightings s
group by s.person, s.name;

select sig.person, max(sig.date) date_finish
from sig
group by sig.person
having count(distinct sig.name) >=
	(select count(distinct fl.comname)
    from flowers fl);

drop view if exists sig;
/*
person, date_finish
----------
Maria	2006-09-23
*/

#12. Which latitude range (defined by a lower latitude and an upper latitude) having no more than 20 different locations inside of it 
#had the most flower sightings, and how many sightings were there?
drop view if exists ranges_loc;
drop view if exists ranges_sig;

create view ranges_loc as
select fe1.latitude lower, fe2.latitude upper, count(distinct fe3.location) loc_count
from features fe1, features fe2, features fe3
where fe1.latitude <= fe2.latitude
	and fe3.latitude between fe1.latitude and fe2.latitude
group by fe1.latitude, fe2.latitude
having loc_count <= 20;

create view ranges_sig as
select rl.lower, rl.upper, count(*) sig_count
from ranges_loc rl, sightings s, features fe
where fe.location = s.location 
	and fe.latitude between rl.lower and rl.upper
group by rl.lower, rl.upper;

select *
from ranges_sig rs1
where rs1.sig_count >= 
	(select max(rs2.sig_count)
    from ranges_sig rs2)
order by rs1.lower, rs1.upper;
    
drop view if exists ranges_loc;
drop view if exists ranges_sig;
/*
lower, upper, sig_count
----------
352704	353748	233
352801	354430	233
*/


