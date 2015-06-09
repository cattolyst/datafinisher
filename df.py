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
	wrds = words.split(); lens = map(len,wrds); idxs=range(len(lens))
	""" sort the indexes and lengths"""
	idxs.sort(key=lambda xx: lens[xx]); lens.sort()
	""" initialize the threshold and the vector of 'most important' words"""
	sumidx=0; keep=[]
	while sumidx < limit:
		sumidx += lens.pop()
		keep.append(idxs.pop())
	keep.sort()
	shortened = [wrds[ii] for ii in keep]
	return shortened

def dropletters(intext):
	return re.sub(r"([a-z])\1",r"\1",re.sub("\B[aeiouyAEIOUY]+","",re.sub("[^a-zA-Z0-9 _]","","_".join(intext))))

if __name__ == '__main__':
    print dropletters(shortenwords('Closed treatment of distal radial fracture (eg, Colles or Smith type) or epiphyseal separation, includes closed treatment of fracture of ulnar styloid, when performed; without manipulation',50))

