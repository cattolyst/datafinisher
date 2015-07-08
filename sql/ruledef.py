def ruledef_read():
	cnx.execute("DROP TABLE IF EXISTS ruledefs")
	cnx.execute("CREATE TABLE ruledefs (sub_slct_std UNKNOWN_TYPE_STRING, sub_payload UNKNOWN_TYPE_STRING, sub_frm_std UNKNOWN_TYPE_STRING, sbwr UNKNOWN_TYPE_STRING, sub_grp_std UNKNOWN_TYPE_STRING, presuffix UNKNOWN_TYPE_STRING, suffix UNKNOWN_TYPE_STRING, concode UNKNOWN_TYPE_BOOLEAN NOT NULL, rule UNKNOWN_TYPE_STRING NOT NULL, grouping INTEGER NOT NULL, subgrouping INTEGER NOT NULL, in_use UNKNOWN_TYPE_BOOLEAN NOT NULL)")

	with open('ruledefs.csv','rb') as fin: 
    	# csv.DictReader uses first line in file for column headings by default
	    dr = csv.DictReader(fin) # comma is default delimiter
    	to_db = [(i['col1'], i['col2'], i['col3'], i['col4'], i['col5'], i['col6'], i['col7'], i['col8'], i['col9'], i['col10'], i['col11'], i['col12'],) for i in dr]

	cur.executemany("INSERT INTO ruledefs (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
	cnx.commit()
if __name__ == '__main__':
	ruledef_read()