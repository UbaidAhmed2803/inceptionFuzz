import sharedData

def createDirectory():
	#Stripping the url for naming the file as domain name
	sharedData.domain = urlparse(sharedData.url).netloc

	#Creating a directory within Results directory
	Path("Results/"+domain).mkdir(parents=True, exist_ok=True)

def openFiles():
	#Opening a file for writing results
	sharedData.resultFile=open('Results/'+sharedData.domain+'/results_'+str(sharedData.fuzzCounter)+'.txt','a') #Appends at the last

	#Opening a file for writing non 404 directories
	sharedData.non404File=open('Results/'+sharedData.domain+'/non404_'+str(sharedData.fuzzCounter)+'.txt','a') #Appends at the last

	#Opening a file for storing any URL which resulted in error
	sharedData.errorFile=open('Results/'+sharedData.domain+'/error_'+str(sharedData.fuzzCounter)+'.txt','a') #Appends at the last

def closeFiles():
	sharedData.resultFile.close() #To save the result of first level fuzz in case of a crash
	sharedData.non404File.close() #Closing to prevent loss of data if there is a crash during second level fuzzing
	sharedData.errorFile.close() 


def store(result,payload):
	sharedData.requestsSent+=1
	if(str(result.status_code)!="404"): #Storing the urls giving non 404 directories
		# print("I am here")
		sharedData.not404directories.append(payload)
		sharedData.non404File.write(str(result.status_code)+" : "+sharedData.url+"/"+payload)

	if(sharedData.statusFlag and str(result.status_code) in sharedData.statusShow):
		result=sharedData.url+"/"+payload.strip()+"\t\t"+str(result.status_code)
		sharedData.resultFile.write(result+"\n")
		print(result)
	elif(sharedData.statusFlag and str(result.status_code) not in sharedData.statusShow):
		if(result.status_code==404):
			# Skip
			return
	elif(sharedData.statusFlag == 0):
		result=sharedData.url+"/"+payload.strip()+"\t\t"+str(result.status_code)
		sharedData.resultFile.write(result+"\n")
		print(result)
		



