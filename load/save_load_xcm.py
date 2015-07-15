# pyxspec
def save_as_xcm(filename,s_type="all"):
	'''saves stat,method,abund,xsect,cosmo,delta,systematic,model and parameters to an xcm file'''
	if len(filename.split("."))>1 and filename.split(".")[-1]=="xcm":
		ext=""
	else:
		ext=".xcm"
	fw_xcm=open(filename+ext,"w")
	fw_xcm.write("statistic "+str(Fit.statMethod)+"\n")
	fw_xcm.write("method "+str(Fit.method)+" "+str(Fit.nIterations)+" "+str(Fit.criticalDelta)+"\n")
	fw_xcm.write("abund "+str(Xset.abund)+"\n")
	fw_xcm.write("xsect "+str(Xset.xsect)+"\n")
	fw_xcm.write("cosmo "+str(Xset.cosmo[0])+" "+str(Xset.cosmo[1])+" "+str(Xset.cosmo[2])+"\n")
	fw_xcm.write("xset delta "+str(Fit.delta)+"\n")
	fw_xcm.write("systematic "+str(AllModels.systematic)+"\n")
	if s_type=="all" or s_type=="files":
		ignore_str=""
		for x in range(1,AllData.nSpectra+1):
			s=AllData(x)
			fw_xcm.write("data "+str(x)+":"+str(x)+" "+s.fileName+"\n")
			if 	not s.ignoredString()=="":
				ignore_str+=str(x)+":"+s.ignoredString().replace(" ",",")+" "
		fw_xcm.write("ignore "+ignore_str+"\n")
	if s_type=="all" or s_type=="model":	
		THEMODEL=AllModels(1)
		newpars=""
		fw_xcm.write("model "+THEMODEL.expression+"\n")
		for n in range(1,AllData.nGroups+1):
			c_m=AllModels(n)
			for k in range(1,c_m.nParameters+1):
				c_p=c_m(k)
				if c_p.link=="":
					fw_xcm.write(str(c_p.values[0])+" "+str(c_p.values[1])+" "+str(c_p.values[2])+" "+str(c_p.values[3])+" "+str(c_p.values[4])+" "+str(c_p.values[5])+"\n")
				else:
					param=(c_m.nParameters*(n-1))+k
					link=c_p.link
					print link,link.split("=")[-1],param,int(link.split("=")[-1])>int(param)
					if int(link.split("=")[-1])>int(param):
						fw_xcm.write("/\n")
						newpars+="newpar "+str(param)+" "+c_p.link+"\n"
					else:
						fw_xcm.write(c_p.link+"\n")
		fw_xcm.write(newpars)

def load_xcm(filename):
	'''loads xcm file into pyxspec env'''
	model_flag=False
	model_param_counter=1
	model_num=1
	for cmd in open(filename):
		cmd=cmd.replace("\n","")
		if model_flag==True:
			cmd=re.sub("\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)","\g<1> \g<2> \g<3> \g<4> \g<5> \g<6>",cmd).split(" ")
			m=AllModels(model_num)
			p=m(model_param_counter)
			if "/" in cmd:
				model_param_counter+=1
				if model_param_counter>m.nParameters:
					model_num+=1
					model_param_counter=1
					if model_num>AllData.nGroups:
						model_flag=False
				continue
			elif "=" in cmd:
				p.link="".join(cmd).replace("=","")
			else:
				p.values=map(float,[ z for z in cmd if not z==''])

			model_param_counter+=1
			if model_param_counter>m.nParameters:
				model_num+=1
				model_param_counter=1

				if model_num>AllData.nGroups:
					model_flag=False
		else:
			cmd=cmd.split(" ")
			if cmd[0]=="statistic":
				Fit.statMethod=cmd[1]
			elif cmd[0]=="method":
				Fit.method=cmd[1]
				Fit.nIterations=int(cmd[2])
				Fit.criticalDelta=float(cmd[3])
			elif cmd[0]=="abund":
				Xset.abund=cmd[1]
			elif cmd[0]=="xsect":
				Xset.xsect=cmd[1]
			elif cmd[0]=="xset":
				if cmd[1]=="delta":
					Fit.delta=float(cmd[2])
			elif cmd[0]=="systematic":
					AllModels.systematic=float(cmd[1])
			elif cmd[0]=="data":
				AllData(" ".join(cmd[1:]))
			elif cmd[0]=="ignore":
				AllData.ignore(" ".join(cmd[1:]))
			elif cmd[0]=="model":
				model_flag=True
				Model(" ".join(cmd[1:]))
			elif cmd[0]=="newpar":
				m=AllModels(1)
				npmodel=m.nParameters #number of params in model
				group=int(np.ceil((float(cmd[1]))/npmodel))

				if not int(cmd[1])/npmodel==float(cmd[1])/npmodel:
					param=int(cmd[1])-(int(cmd[1])/npmodel)*npmodel # int div so effectivly p-floor(p/npmodel)*npmodel
				else:
					param=npmodel
				
				print group,param
				
				m=AllModels(group)
				p=m(param)
				
				if "=" in cmd[2] :
					p.link="".join(cmd[2:]).replace("=","")
				else:
					p.values=map(float,cmd[2:])
