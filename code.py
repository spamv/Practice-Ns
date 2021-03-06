import sys
import os
import math
import argparse

ALPHA=(1/float(8))

#RETURN INFORMATION PARSED BY SEQUENCE NUMBER
def read(data,filename):
	jamoti=[]
	f=open(filename,"r")
	for line in f:
		if line.split()[7]=='1':
			if int(line.split()[10]) not in data.keys():
				data[int (line.split()[10])]=jamoti
			data[int (line.split()[10])].append(line.split())
			jamoti=[]
	f.close()

#GET START AND FINISH CONVERSATION => DEPRECATED
def startfinish(data):
	foundack={}
	for seq in data:
		booltcp=True
		boolack=True
		for l in data[seq]:
			if l[0]=='-' and booltcp==True:
				m='seq'+l[10]+'ns'+l[3]+'nd'+l[2]+'tack'
				foundack[m]=l
				startc.append(l)
				booltcp=False
			if l[0]=='r' and boolack==True:
				n='seq'+l[10]+'ns'+l[2]+'nd'+l[3]+'t'+l[4]
				if n in foundack.keys():
					finishc.append(l)
					boolack=False

#GET START AND FINISH CONVERSATION
def startfinishTwo(data):
	foundacktwo={}
	for seq in data:
		booltcp=True
		boolack=True
		for l in data[seq]:
			if l[0]=='-' and booltcp==True:
				m='seq'+l[10]+'ns'+l[3]+'nd'+l[2]+'tack'
				foundacktwo[m]=l
				startctwo.append(l)
				finishctwo.append(0)
				booltcp=False
			if l[0]=='r' and boolack==True:
				n='seq'+l[10]+'ns'+l[2]+'nd'+l[3]+'t'+l[4]
				if n in foundacktwo.keys():
					finishctwo.pop()
					finishctwo.append(l)
					boolack=False

#COMPUTE RTT
def rtt_f(startc,finishc,finishctwo):
	for it in range(len(finishctwo)):
		if finishctwo[it]==0:
			rtt.append(rtt[-1])
		else:	
			rtt.append(float(finishctwo[it][1])-float(startctwo[it][1]))

#COMPUTE RTT ESTIMATED AND TIMEOUT FROM ORIGINAL ALGORITHM
def rttestimated_f(rtt):
	rtte = 0
	rttestimated.append(0)
	timeout.append(0)
	for itrtt in rtt:
		rtte=((1-ALPHA)*float(itrtt))+(float(rtte)*ALPHA)
		rttestimated.append(rtte)
		timeout.append(float(rtte)*2)

#COMPUTE RTT ESTIMATED AND TIMEOUT FROM JACOBSON/KARELS ALGORITHM
def rttestimated_jak_f(rtt):
	rtte = 0
	rttestimated_jak.append(0)
	timeout_jak.append(0)
	desv=0
	for itrtt in rtt:
		diff=float(itrtt)-float(rtte)
		rtte=rtte+((1/float(4))*float(diff))
		rttestimated_jak.append(rtte)
		desv=float(desv)+((1/float(4)*(math.sqrt(diff*diff)-float(desv))))
		timeout=float(rtte)+(4*float(desv))
		timeout_jak.append(timeout)
		#print rtte,timeout

#COMPUTE RTT ESTIMATED AND TIMEOUT FROM KARN/PATRIDGE ALGORTIHM
def rttestimated_kar_f(rtt):
	rtte = 0
	rttestimated_kar.append(0)
	timeout_kar.append(0)
	i=0
	for itrtt in rtt:
		i=i+1
		rtte=((1-ALPHA)*float(itrtt))+(float(rtte)*ALPHA)
		rttestimated_kar.append(rtte)
		if finishctwo[(i-1)]==0:
			timeout_kar.append(timeout_kar[-1])
		else:
			if finishctwo[(i-1)][10] in retransmsegments.keys():	
				timeout_kar.append(float(rtte)*2*2)
			else:
				timeout_kar.append(float(rtte)*2)

#GET RETRANSMITED PACKAGES AND RETRANSMITED SEGMENTS
def retransmited_pack():
	for jj in data:
		for hh in data[jj]:
			if hh[0]=='-':
				m='seq'+hh[10]+'ns'+hh[2]+'nd'+hh[3]+'t'+hh[4]
				if m not in allpack.keys():
					allpack[m]=hh
				else:
					retransm.append(hh)
					retransmsegments[hh[10]]=1
					#print hh

#GET OVERSTEPPED TIMEOUT PACKETS
def oversteppedTimeout():
	for it in range(len(rtt)):
		if rtt[it]>timeout[it] and it!=0: 
			#m='seq'+finishc[it][10]+'ns'+finishc[it][2]+'nd'+finishc[it][3]+'t'+finishc[it][4]
			#overstepped.append(float(startc[it][1])+float(timeout[it]))
			overstepped.append(float(startc[it][1])+float(timeout[it]))
			#print m

#RETURN INFORMATION PARSED BY ORDER
def readcont(datacont,filename):
	jamoti=[]
	ff=open(filename,"r")
	i=0
	for line in ff:
		i=i+1
		if line.split()[7]=='1':
			datacont[i-1]=jamoti
			datacont[i-1].append(line.split())
			jamoti=[]
	ff.close()

#COMPUTE CONGESTION WINDOW WITH ORIGINAL ALGORITHM
def congestionWindow_o():
	cwnd_o.append(1)
	cwnd_o_time.append(0)
	overstepped_cop=overstepped[:]
	for lin in datacont:
		cwnd_o_time.append(datacont[lin][0][1])
		cwnd_o.append(cwnd_o[-1])
		if datacont[lin][0][4]=='ack' and datacont[lin][0][0]=='r':
			cwnd_o.pop()
			cwnd_o.append(40)
		if len(overstepped_cop)>0 and float(datacont[lin][0][1])>float(overstepped_cop[0]):
			cwnd_o.pop()
			cwnd_o.append(1)
			overstepped_cop.pop(0)

#COMPUTE CONGESTION WINDOW WITH ADDITIVE INCREASE/MULTIPLICATIVE DECREASE
def congestionWindow_aimd():
	cwnd_aimd.append(1)
	cwnd_aimd_time.append(0)
	overstepped_cop=overstepped[:]
	cwmax=40
	cwini=1
	for lin in datacont:
		cwnd_aimd_time.append(datacont[lin][0][1])
		cwnd_aimd.append(cwnd_aimd[-1])
		if datacont[lin][0][4]=='ack' and datacont[lin][0][0]=='r':
			if int(cwnd_aimd[-1])<cwmax:
				cwnd_aimd.pop()
				cwnd_aimd.append(cwmax)
			else:
				m=float(cwnd_aimd[-1])+(1/float(cwnd_aimd[-1]))
				cwnd_aimd.pop()
				cwnd_aimd.append(m)
		if len(overstepped_cop)>0 and float(datacont[lin][0][1])>float(overstepped_cop[0]):
			cwnd_aimd.pop()
			cwnd_aimd.append(cwini)
			cwmax=cwmax/2
			overstepped_cop.pop(0)

#COMPUTE CONGESTION WINDOW WITH SLOW START
def congestionWindow_ss():
	cwnd_ss.append(1)
	cwnd_ss_time.append(0)
	overstepped_cop=overstepped[:]
	cwmax=40
	cwini=1
	for lin in datacont:
		cwnd_ss_time.append(datacont[lin][0][1])
		cwnd_ss.append(cwnd_ss[-1])
		if datacont[lin][0][4]=='ack' and datacont[lin][0][0]=='r':
			if int(cwnd_ss[-1])<cwmax:
				n=float(cwnd_ss[-1])+1
				cwnd_ss.pop()
				cwnd_ss.append(n)
			else:
				m=float(cwnd_ss[-1])+(1/float(cwnd_ss[-1]))
				cwnd_ss.pop()
				cwnd_ss.append(m)
		if len(overstepped_cop)>0 and float(datacont[lin][0][1])>float(overstepped_cop[0]):
			cwnd_ss.pop()
			cwnd_ss.append(cwini)
			cwmax=cwmax/2
			overstepped_cop.pop(0)

#PLOT TIME OUT ALGORITHMS
def plottimeout(rtt,timeout,timeout_kar,timeout_jak,rttestimated):
		fig = plt.figure()
		ax1 = fig.add_subplot(211)
		rtt,=ax1.plot(rtt,'r.')
		#rttestimated,=plt.plot(rttestimated)
		if args.type=="or_to" or args.type=="all":
			timeout,=ax1.plot(timeout)
		if args.type=="kar" or args.type=="all":
			timeout_kar,=ax1.plot(timeout_kar)
		if args.type=="jak" or args.type=="all":
			timeout_jak,=ax1.plot(timeout_jak)
		plt.ylabel('Seconds')
		plt.xlabel('Sequence number')
		plt.legend([rtt,timeout,timeout_kar,timeout_jak], ["RTT","TIMEOUT ORI","TIMEOUT KAR","TIMEOUT JAK"])
		
		if args.fr!=None:
			ax2 = fig.add_subplot(212)
			rtt_rtt_file.pop(0)
			rtt_rtt_file.pop(0)
			to_rtt_file.pop(0)
			to_rtt_file.pop(0)
			ax2.plot(rtt_rtt_file,'r.')
			ax2.plot(to_rtt_file)
			plt.ylabel('Seconds')
			plt.xlabel('Seconds')
			plt.legend([rtt,timeout,timeout_kar,timeout_jak], ["RTT","TIMEOUT ORI","TIMEOUT KAR","TIMEOUT JAK"])

		plt.show()

#PLOT CONGESTION WINDOW ALGORITHMS
def plotcongestionw(cwnd_o,cwnd_o_time,cwnd_aimd,cwnd_aimd_time,cwnd_ss,cwnd_ss_time,cw_rtt_file):
		fig = plt.figure()
		ax1 = fig.add_subplot(211)
		if args.type=="or_cw" or args.type=="all":
			m=max(cwnd_o)+5
			cwnd_o,=ax1.plot(cwnd_o_time,cwnd_o)
		if args.type=="aimd" or args.type=="all":
			m=max(cwnd_aimd)+5
			cwnd_aimd,=ax1.plot(cwnd_aimd_time,cwnd_aimd)
		if args.type=="ss" or args.type=="all":
			m=max(cwnd_ss)+5
			cwnd_ss,=ax1.plot(cwnd_ss_time,cwnd_ss)
		plt.ylabel('MMS')
		plt.ylim([0,m])
		plt.xlabel('Seconds')
		plt.legend([cwnd_o,cwnd_aimd,cwnd_ss], ["ORIG","AI/MD","SLOW"])

		if args.fr!=None:
			ax2 = fig.add_subplot(212)
			ax2.plot(t_rtt_file, cw_rtt_file)
			plt.ylabel('MMS')
			#plt.ylim([0,80])
			plt.xlabel('Seconds')
			plt.legend([cwnd_o,cwnd_aimd,cwnd_ss], ["ORIG","AI/MD","SLOW"])

		plt.show()

#PRINT TIMEOUT FOR PRINTT ARGUMENT
def print_to(listt):
	for i in listt:
		print i

#PRINT CONGESTION WINDOW FOR PRINTT ARGUMENT
def print_cw(cwnd,cwndt):
	for i in range(len(cwnd)):
		print cwndt[i],cwnd[i]

#PARSE RTT FILES TO COMPARE
def parseRttFiles(cw_rtt_file,t_rtt_file,rtt_rtt_file,to_rtt_file,filename):
	v=open(filename,"r")
	for line in v:
		cw_rtt_file.append(line.split()[5])
		t_rtt_file.append(line.split()[0])
		rtt_rtt_file.append(line.split()[1])
		to_rtt_file.append(line.split()[3])
	v.close()


if __name__ == "__main__":

	#PARSER CONFIGURATION FOR ARGUMENTS USE
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", help="enter .tr file")
	parser.add_argument("-fr", help="enter .rtt file (opcional)")
	parser.add_argument("-plot", help="[cw] to plot congestion window, [to] to plot time out")
	parser.add_argument("-type", help="[or_to] to plot original, [kar] to plot Karn/Patridge, [jak] to plot Jacobson/Karels, [or_cw] to plot original,[aimd] to plot AI/MD, [ss] to plot SlowStart, [all] to plot all")
	parser.add_argument("-printt", help="[or_to] to print original, [kar] to print Karn/Patridge, [jak] to print Jacobson/Karels, [aimd] to print AI/MD, [ss] to print SlowStart")
	args = parser.parse_args()

	#HELF IF NO .TR FILE INPUT
	if args.f==None:
		print sys.argv[0], "[-h]  to enter help menu"
		sys.exit()

	#PARSE IF .RTT FILE INPUT
	if args.fr!=None:
		cw_rtt_file=[]
		t_rtt_file=[]
		rtt_rtt_file=[]
		to_rtt_file=[]
		parseRttFiles(cw_rtt_file,t_rtt_file,rtt_rtt_file,to_rtt_file,args.fr)

	#IMPORT MATPLOTLIB IF ITS REQUIRED
	if args.plot!=None:
		import matplotlib.pyplot as plt

	#PACKAGES PARSET BY SEGMENT
	data={}
	read(data,args.f)

	#START AND FINISH POINTS OF TRACE => DEPRECATED
	startc=[]
	finishc=[]
	startfinish(data)

	#START AND FINISH POINTS OF TRACE
	startctwo=[]
	finishctwo=[]
	startfinishTwo(data)

	#RTT
	rtt=[]
	rtt_f(startc,finishc,finishctwo)

	#RTT ESTIMATED ORIGINAL
	rttestimated=[]
	timeout=[]
	rttestimated_f(rtt)

	#FUNCTIONS FOR PRINTT ARGUMENT
	if args.printt=="or_to":print_to(timeout)
	if args.printt=="jak":print_to(timeout_jak)
	if args.printt=="kar":print_to(timeout_kar)
	if args.printt=="or_cw":print_to(cwnd_o,cwnd_o_time)
	if args.printt=="aimd":print_cw(cwnd_aimd,cwnd_aimd_time)
	if args.printt=="ss":print_to(cwnd_ss,cwnd_ss_time)

	#RETRANSMITTED PACKAGES
	allpack={}
	retransmsegments={}
	retransm=[]
	retransmited_pack()

	#OVERESTEPED TIME OUT
	overstepped=[]
	overstepped_cop=[]
	oversteppedTimeout()

	#RTT ESTIMATED KARN/PATRIDGE
	rttestimated_kar=[]
	timeout_kar=[]
	rttestimated_kar_f(rtt)
	if args.printt=="kar":print_to(timeout_kar)

	#RTT ESTIMATED JACOBSON/KARELS
	rttestimated_jak=[]
	timeout_jak=[]
	rttestimated_jak_f(rtt)
	if args.printt=="jak":print_to(timeout_jak)

	#PLOT TIME OUT ALGORITHMS
	if args.plot=='to':
		plottimeout(rtt,timeout,timeout_kar,timeout_jak,rttestimated)

	#-------------------------CONGESTION WINDOW

	#PACKAGES PARSED BY TIME
	datacont={}
	readcont(datacont,args.f)

	#CONGESTION WINDOW WITH ORIGINAL ALGORITHM
	cwnd_o=[]
	cwnd_o_time=[]
	congestionWindow_o()
	if args.printt=="or_cw":print_cw(cwnd_o,cwnd_o_time)
	
	#CONGESTION WINDOW WITH ADDITIVE INCREASE/MULTIPLICATIVE DECREASE
	cwnd_aimd=[]
	cwnd_aimd_time=[]
	congestionWindow_aimd()
	if args.printt=="aimd":print_cw(cwnd_aimd,cwnd_aimd_time)

	#CONGESTION WINDOW WITH SLOW START
	cwnd_ss=[]
	cwnd_ss_time=[]
	congestionWindow_ss()
	if args.printt=="ss":print_cw(cwnd_ss,cwnd_ss_time)

	#PLOT CONGESTION WINDOW ALGORITHMS
	if args.plot=='cw':
		plotcongestionw(cwnd_o,cwnd_o_time,cwnd_aimd,cwnd_aimd_time,cwnd_ss,cwnd_ss_time,cw_rtt_file)

	
