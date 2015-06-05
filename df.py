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

