from time import time
import csv
import os
import subprocess
import numpy as np

# Changes calls format. Previous format for each line is 'APICallX'===>['NextCall1','NextCall2'...] according to all the times APICallX is called. The resulting file will have each line as 'APICallX'\t'NextCall1'\t'NextCall2'\t...
def main (WHICHSAMPLES,wf):
	alldb=[]
	allapps=[]
	for v in range (0,len(WHICHSAMPLES)):
		onedb=[]
		numApps=os.listdir('graphs/'+WHICHSAMPLES[v]+'/')

		allapps.append(numApps)
		leng=len(numApps)
		Fintime=[]
		checks=[0,999,1999,2999,3999,4999,5999,6999,7999,8999,9999,10999,11999,12999]
		for i in range (0,len(numApps)):
			if i in checks:
				print 'starting ',i+1,' of ',leng
			with open('graphs/'+WHICHSAMPLES[v]+'/'+str(numApps[i])) as callseq:
				specificapp=[]
				for line in callseq:
						specificapp.append(line)
				callseq.close()

			call=[]
			nextblock=[]
			nextcall=[]
			Startime= time()
			for line in specificapp:
				if (line[0]=='<' and (line[1]=="'" or line[1].isalpha())):
					call.append(str(line.split('(')[0]))
					nextblock.append(str(line.split('==>')[1]))

			for j in range (0,len(nextblock)):

				supporto=nextblock[j].translate(None, '[]\'\\')
				supporto=supporto.replace('\n','')

				nextcall.append([])
				nextcall[j]=(supporto.split(','))

                                #if len(nextcall[j])>1:
                                #    print "%s" % supporto
                                #    print "%s" % nextcall[j]

			Fintime.append(time()-Startime)
			wholefile=[]
			for j in range (0, len(call)):
				eachline=call[j]+'\t'
                                #if len(nextcall[j])>1:
                                #    print "%s, len=%d" % (call[j],len(nextcall[j]))

				for k in range (0,len(nextcall[j])):
					tagliaparam=nextcall[j][k].split('(')[0]
					eachline=eachline+tagliaparam+'\t'

				wholefile.append(eachline)

			if wf=='Y':
				f = open('Calls/'+WHICHSAMPLES[v]+'/'+str(numApps[i]), 'w')
				for line in wholefile:
					f.write(str(line)+'\n')
				f.close
			onedb.append(wholefile)
		alldb.append(onedb)
	return alldb,allapps

