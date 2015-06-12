"""
Figuring out how to shorten names extracted from the variable table in the databuilder output
"""
import sqlite3 as sq,sys,re,string;

# TODO: interpret command-line arguments like makesql.py does
# TODO: either move these functions to the main code or figure out how to package them as a library/extension/whatever

""" Here is how to find the length of each word in a string """
# [len(ii) for ii in "Aftercare following surgery system NEC".split()]
""" Then we find the max and min, iterate from max to min
For every word of length ii, add ii to the score, an at the same time pop the largest index out of the array
When score exceeds target length, break out of the loop before popping the corresponding index
Order the indexes and extract the corresponding words"""

def shortenwords(words,limit):
	""" Initialize the data, lengths, and indexes"""
	#words = str(words)
	print words
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

def dropletters(intext):
	return re.sub(r"([a-z])\1",r"\1",re.sub("\B[aeiouyAEIOUY]+","",re.sub("[^a-zA-Z0-9 _]","", intext)))

if __name__ == '__main__':
    print dropletters(shortenwords('Closed treatment of distal radial fracture (eg, Colles or Smith type) or epiphyseal separation, includes closed treatment of fracture of ulnar styloid, when performed; without manipulation',50))
    con = sq.connect('pedobese_bos.db')
    con.create_function("sw",2,shortenwords)
    con.create_function("dl",1,dropletters)
    cur = con.cursor()
    cur.execute("select sw(name,30) from variable where length(name) > 40")
    foo = cur.fetchall()
    cur.execute("select 'v'||substr('000'||id,-3,3)||'_'||replace(dl(sw(name,30)),' ','_') from variable where length(name)> 40")
    baz = cur.fetchall()
    # awesome: semi-human-readable fields are implemented
    cur.execute("update data_dictionary set colid =  colid||'_'||replace(dl(sw(name,30)),' ','_')")
    bar = cur.fetchall()
    cur.execute("select name from data_dictionary")
    baz = cur.fetchall()
    import pdb; pdb.set_trace()
    
