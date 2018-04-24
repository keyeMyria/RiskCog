#!/usr/bin/python 

import sys

if len(sys.argv) != 3:
	print ("ps.py inputFile outputFile")
	exit()

iput = open(sys.argv[1],'r')
oput = open(sys.argv[2],'w')
lines = iput.readlines()

lines = [st for st in lines if not (st.startswith("@") or len(st.strip()) == 0)]
datas = [st.split() for st in lines]

for data in datas:
    print>> oput, data[-2],' ',
    for i, num in enumerate(data[:-2]):
         print >> oput, ("%s:%s"%(i,num)),' ',
    print  >> oput

iput.close()
oput.close()
