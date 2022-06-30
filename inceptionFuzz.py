# Python code to fuzz a curl request
import requests
import sys
import re
from urllib.parse import urlparse
import pyfiglet

print("\n")
print("****************************************************************\n")  
result = pyfiglet.figlet_format("inceptionFuzz")
print(result)
print("****************************************************************\n")
print("***********************By UbaidAhmed.com************************\n")
print("****************************************************************\n")
print("\n")
print("Performing few checks before fuzzing.......\n")

#Reading the domain name provided as command line argument
urlArg = sys.argv[1]
print("URL: "+urlArg)
url = urlArg.strip()


#Creating a list of all the command line arguments.
parameters = sys.argv
#Removing the filename and domain from the list
del parameters[0:2]


# paramCount = 1
headers = []
headerList =[]
headerValueList = []
headerFlag = 0
statusFlag=0
statusShow = []
wordListFlag=0
wordListPath=""
headerAndValue=[]


#Reading and storing params based on the options choosen by the user

for params in parameters:
	if(params ==  "--status"):
		statusFlag=1
	elif(statusFlag and params!="--status" and len(statusShow)<1):
		statusShow=params.split(",")
		print("Show Status: "+str(statusShow))

	elif(params == "--headers"):
		headerFlag=1

	elif(params == "--wordlist"):
		wordListFlag=1

	elif(headerFlag and params!="--headers" and wordListFlag==0):
		headers.append(params)

	elif(wordListFlag and params != "--wordlist"):
		wordListPath=params


#Each header and its value is being saved as single List item
for headerSplit in headers:
	headerList.append(headerSplit.split(":",1)[0])
	headerValueList.append(headerSplit.split(":",1)[1])
	
headerCount = len(headerList)

if(headerFlag):
	print("Headers: "+str(headers))

if(wordListFlag):
	print("Wordlist: "+str(wordListPath))

urlVerifyRegex=("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

urlVerification = re.compile(urlVerifyRegex)

if(re.search(urlVerification,url)):
	validUrl=bool(True)
else:
	validUrl=bool(False)
	print("Please provide a proper URL starting with either http:// or https://")
	quit()

print("All looks good. Time to Fuzz....\n")

#Reading the payload file from command line if it is provided else using default wordlist
if(wordListFlag==1):
	payloadsFile = open(wordListPath, 'r')	
else:
	payloadsFile = open('wordlists/36KCommonDirectoryAndFileNames.txt')

fuzz = payloadsFile.readlines()

#Check if the url ends with / and if it does remove /
last_char=url[-1]
if(last_char=="/"):
	url=url.rstrip(url[-1])


# print("Fuzzing : "+url)
print("URL\t\t\t\tStatus Code")
count1 = 0
count2 = 0

#Stripping the url for naming the file as domain name
domain = urlparse(url).netloc

#Opening a file for writing results
resultFile=open(domain+'.txt','a') #Appends at the last

# Strips the newline character
for payload1 in fuzz:
		count1 += 1
		if(headerCount==0):
			res=requests.get(url+"/"+payload1.strip())
		elif(headerCount==1):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0]})
		elif(headerCount==2):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1]})
		elif(headerCount==3):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1],headerList[2]:headerValueList[2]})
		
		if(statusFlag and str(res.status_code) in statusShow):
			result=url+"/"+payload1.strip()+"\t\t"+str(res.status_code)
			resultFile.write(result+"\n")
			print(result)
		elif(statusFlag == 0):
			result=url+"/"+payload1.strip()+"\t\t"+str(res.status_code)
			resultFile.write(result+"\n")
			print(result)	

		
		for payload2 in fuzz:
			count2 += 1
			if(headerCount==0):
				res=requests.get(url+"/"+payload1.strip()+"/"+payload2.strip())
			elif(headerCount==1):
				res=requests.get(url+"/"+payload1.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0]})
			elif(headerCount==2):
				res=requests.get(url+"/"+payload1.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1]})
			elif(headerCount==3):
				res=requests.get(url+"/"+payload1.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1],headerList[2]:headerValueList[2]})


			if(statusFlag and str(res.status_code) in statusShow):
				result=url+"/"+payload1.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
				resultFile.write(result+"\n")
				print(result)
			elif(statusFlag == 0):
				result=url+"/"+payload1.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
				resultFile.write(result+"\n")
				print(result)

			print("Fuzzing : "+ url+"/"+payload1.strip()+"/"+payload2.strip()+"\t"+str(res.status_code),end='\r')			
				
resultFile.close()
payloadsFile.close()


print("Reached the end of payload file. Bye!!\n")

