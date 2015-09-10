import sqlite3 as sq,argparse,re,csv,time,ConfigParser,pdb

###############################################################################
# Functions and methods to use within SQLite                                  #
###############################################################################

# okay, this actually works
class diaggregate:
  def __init__(self):
    self.cons = {}
    self.oocm = {}; self.ooc = []
  def step(self,con,mod):
    if con not in self.cons.keys():
      self.cons[con] = [mod]
    else:
      if mod not in self.cons[con]:
	self.cons[con].append(mod)
  def finalize(self):
    for ii in self.cons:
      iimods = [jj for jj in self.cons[ii] if jj not in  ['@',None,'']]
      if len(iimods) == 0:
	self.ooc.append('"'+ii+'"')
      else:
	self.oocm[ii] = iimods
    #oo += ['"'+ii+'":["'+'","'.join(self.cons[ii])+'"]' for ii in self.cons]
    #oo = ",".join(oo)
    return ",".join(self.ooc+['"'+ii+'":["'+'","'.join(self.oocm[ii])+'"]' for ii in self.oocm])
  
# generically jam together the ancillary fields to see if there is anything 
# noteworthy anywhere in there note that normally you would use NULL or '' for 
# some of these params (to bypass them), doing the aggregation only on the ones 
# you don't expect to see
class infoaggregate:
  def __init__(self):
    self.cons = {}
  def step(self,con,mod,ins,vtp,tvc,nvn,vfl,qty,unt,loc,cnf):
    self.ofvars = {'cc':str(con),'mc':str(mod),'ix':str(ins),'vt':str(vtp),'tc':str(tvc),'vf':str(vfl),'qt':str(qty),'un':str(unt),'lc':str(loc),'cf':str(cnf)}
    # go through each possible arg, check if it's NULL/@/''
    # if not, add to self.cons
    if nvn not in ['@','None',None,'']:
      if 'nv' not in self.cons.keys():
	self.cons['nv'] = 1
      else:
	self.cons['nv'] += 1
    for ii in self.ofvars:
      if self.ofvars[ii] not in ['@','None',None,'']:
	if ii not in self.cons.keys():
	  self.cons[ii] = [self.ofvars[ii]]
	elif self.ofvars[ii] not in self.cons[ii]:
	  self.cons[ii] += [self.ofvars[ii]]
  def finalize(self):
    # oh... python's dictionary format looks just like JSON, and you can convert it to a string
    # the replace calls are just to make it a little more compact
    if 'nv' in self.cons.keys():
      if self.cons['nv']==1:
	del self.cons['nv']
      else:
	self.cons['nv'] = str(self.cons['nv'])
    if 'ix' in self.cons.keys():
      if len(self.cons['ix']) == 1:
      #if self.cons['ix'] == ['1']:
	del self.cons['ix']
    return (str(self.cons)[1:-1]).replace("', '","','").replace(": ",":")

# this is the kitchen-sink aggregator-- doesn't really condense the data, 
# rather the purpose is to preserve everything there is to be known about 
# each OBSERVATION_FACT entry while still complying with the 
# one-row-per-patient-date requirement
class debugaggregate:
  def __init__(self):
    self.entries = []
  def step(self,cc,mc,ix,vt,tc,nv,vf,qt,un,lc,cf):
    self.entries.append(",".join(['"'+ii+'":"'+str(vars()[ii])+'"' for ii in ['cc','mc','ix','vt','tc','nv','vf','qt','un','lc','cf'] if vars()[ii] not in ['@',None,'','None']]))
  def finalize(self):
    return "{"+"},{".join(self.entries)+"}"

# this is to register a SQLite function for pulling out matching substrings 
# (if found) and otherwise returning the original string. Useful for extracting 
# ICD9, CPT, and LOINC codes from concept paths where they are embedded. For 
# ICD9 the magic pattern is:
# '.*\\\\([VE0-9]{3}\.{0,1}[0-9]{0,2})\\\\.*'
def ifgrp(pattern,txt):
    rs = re.search(re.compile(pattern),txt)
    
    if rs == None:
      return txt 
    else:
      return rs.group(1)

# The rdt and rdst functions aren't exactly user-defined SQLite functions...
# They are python function that emit a string to concatenate into a larger SQL query
# and send back to SQL... because SQLite has a native julianday() function that's super
# easy to use. So, think of rdt and rdst as pseudo-UDFs
def rdt(datecol,factor):
    if factor == 1:
      return 'date('+datecol+')'
    else:
      factor = str(factor)
      return 'date(round(julianday('+datecol+')/'+factor+')*'+factor+')'
    
# this one is a wrapper for rdt but with 'start_date' hardcoded as first arg
# because it occurrs so often
def rdst(factor):
    return rdt('start_date',factor)

# Next two are more pseudo-UDFs, that may at some point be used by dd.sql
def dfctday(**kwargs):                                          
  if kwargs is not None:
    oo = "replace(group_concat(distinct '{'||"
    for key,val in kwargs.iteritems():
      oo += """coalesce('{0}:"'||{1}||'",','')||""".format(key,val)
    oo += "'}'),',}','}')"                                             
    return oo
  
def dfctcode(**kwargs):
   if kwargs is not None:
     oo = ""
     for key,val in kwargs.iteritems():
       oo += """coalesce('{0}:['||group_concat(distinct '"'||{1}||'"')||'],','')||""".format(key,val)
     return oo[:-2].replace('],',']')

# Omit "least relevant" words to make a character string shorter
def shortenwords(words,limit):
  """ Initialize the data, lengths, and indexes"""
  #get rid of the numeric codes
  words = re.sub('[0-9]','',words)
  wrds = words.split(); lens = map(len,wrds); idxs=range(len(lens))
  if limit >= len(words):
    return(words)
  """ sort the indexes and lengths"""
  idxs.sort(key=lambda xx: lens[xx]); lens.sort()
  """ initialize the threshold and the vector of 'most important' words"""
  sumidx=0; keep=[]
  # turned out that checking the lengths of the lens and idxs is what it takes to avoid crashes
  while sumidx < limit and len(lens) > 0 and len(idxs) > 0:
    sumidx += lens.pop()
    keep.append(idxs.pop())
  keep.sort()
  shortened = [wrds[ii] for ii in keep]
  return " ".join(shortened)

# This function shortens words by squeezing out vowels, most non-alphas, and 
# repeating letters the first regexp replaces multiple ocurrences of the same 
# letter with one ocurrence of that letter the \B matches a word boundary... 
# so we only remove vowels from inside words, not leading lettters
def dropletters(intext):
  return re.sub(r"([a-z_ ])\1",r"\1",re.sub("\B[aeiouyAEIOUY]+","",re.sub("[^a-zA-Z _]"," ", intext)))

###############################################################################
# Functions used in df.py directly                                            #
###############################################################################

def cleanup(cnx):
    t_drop = ['df_codeid','codefacts','codemodfacts','diagfacts','loincfacts',\
	      'fulloutput','fulloutput2','oneperdayfacts','scaffold','unkfacts',\
	      'unktemp','df_vars','dd2','obs_df','df_rules','data_dictionary']
    v_drop = ['obs_all','obs_diag_active','obs_diag_inactive','obs_labs','obs_noins','binoutput']
    print "Dropping views"
    [cnx.execute("drop view if exists "+ii) for ii in v_drop]
    if len(cnx.execute("pragma table_info(dd2)").fetchall()) >0:
      print "Dropping temporary tables"
      # note that because we're relying on dd2 in order to find the temporary tables, 
      # those have to be dropped before the persistent tables including dd2 get dropped
      [cnx.execute(ii[0]) for ii in cnx.execute("select distinct 'drop table if exists '||ttable from dd2").fetchall()]
    print "Dropping tables"
    [cnx.execute("drop table if exists "+ii) for ii in t_drop]

def tprint(str,tt):
    print(str+":"+" "*(60-len(str))+"%9.4f" % round((time.time() - tt),4))
      

# create the rule definitions table 
# TODO: document the purpose of each column in this table
def create_ruledef(cnx, filename):
	print filename
	cnx.execute("DROP TABLE IF EXISTS df_rules")
	cnx.execute("CREATE TABLE df_rules (sub_slct_std UNKNOWN_TYPE_STRING, sub_payload UNKNOWN_TYPE_STRING, sub_frm_std UNKNOWN_TYPE_STRING, sbwr UNKNOWN_TYPE_STRING, sub_grp_std UNKNOWN_TYPE_STRING, presuffix UNKNOWN_TYPE_STRING, suffix UNKNOWN_TYPE_STRING, concode UNKNOWN_TYPE_BOOLEAN NOT NULL, rule UNKNOWN_TYPE_STRING NOT NULL, grouping INTEGER NOT NULL, subgrouping INTEGER NOT NULL, in_use UNKNOWN_TYPE_BOOLEAN NOT NULL, criterion UNKNOWN_TYPE_STRING)")
	to_db = []
	with open(filename) as csvfile:
	  readCSV = csv.reader(csvfile, skipinitialspace=True)
	  for row in readCSV:
	      to_db.append(row)
	cnx.executemany("INSERT INTO df_rules VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", to_db[1:])
	cnx.commit()
	