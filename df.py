"""
Figuring out how to shorten names extracted from the variable table in the databuilder output
"""
import sqlite3 as sq,sys,re,string;

subpat = re.compile('[^a-zA-z0-9 _]+')

con = sq.connect('/home/a/dx/13_dw.tirado/gpc_obesity/pedobese_bos.db')
cur = con.cursor()
cur.execute('select id,name from variable')
rows = cur.fetchall()
"""Remove all non alphanumeric characters except spaces and then split by spaces
"""
foo=subpat.sub('',rows[20][1]).split()
""" Join first three words with an underscore
"""
print 'v'+str(rows[20][0])+'_'+'_'.join(foo[:3])
""" Join first three and last two words with underscores
"""
print 'v'+str(rows[20][0])+'_'+'_'.join(foo[:3]+foo[-2:])

""" How to remove just the non-leading vowels in a string (\B means not-word-boundary)"""
print re.sub("\B[aeiouyAEIOUY]+","","Outback Steakhouse")
""" And remove duplicated letters """
print re.sub(r"([a-z])\1",r"\1",re.sub("\B[aeiouyAEIOUY]+","","Aftercare following surgery system NEC"))
""" As to which words to keep, http://stackoverflow.com/questions/4105201/create-short-human-readable-string-from-longer-string
Briefly, given a target string length, take words in decreasing length order until length exceeded; drop the one that overshoots;
Return them in their original order of ocurrence. When there are ties, take the right-most word. """
""" Here is how to find the length of each word in a string """
[len(ii) for ii in "Aftercare following surgery system NEC".split()]
""" Then we find the max and min, iterate from max to min
For every word of length ii, add ii to the score, an at the same time pop the largest index out of the array
When score exceeds target length, break out of the loop before popping the corresponding index
Order the indexes and extract the corresponding words"""
wrds = 'Closed treatment of distal radial fracture (eg, Colles or Smith type) or epiphyseal separation, includes closed treatment of fracture of ulnar styloid, when performed; without manipulation'.split()
lens = map(len,wrds);idxs=range(len(lens));idxs.sort(key=lambda xx: lens[xx]);lens.sort();keep=[];sumidx=0
while sumidx < 40:
	sumidx += lens.pop()
	keep.append(idxs.pop())

keep.sort()
shortened = [wrds[ii] for ii in keep]
print re.sub(r"([a-z])\1",r"\1",re.sub("\B[aeiouyAEIOUY]+","",re.sub("[^a-zA-Z0-9 _]","","_".join(shortened))))


