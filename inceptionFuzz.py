# Python code to fuzz a curl request
import requests
import sys
import re
from urllib.parse import urlparse
import pyfiglet
import time

print("\n")
print("****************************************************************\n")  
result = pyfiglet.figlet_format("inceptionFuzz")
print(result)
print("****************************************************************\n")
print("*********************https://ubaidahmed.com*********************\n")
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
not404directories=[]
secondLevelPayloadFuzz = 0


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
	try:
		headerList.append(headerSplit.split(":",1)[0])
		headerValueList.append(headerSplit.split(":",1)[1])
	except:
		print("\nError: Please check the parameters. Something seems to be wrong with them.")
		sys.exit()
	
headerCount = len(headerList)

if(headerFlag):
	print("Headers: "+str(headers))

if(wordListFlag):
	print("Wordlist: "+str(wordListPath))

try:
	requests.get(url)
except:
	print("Error: Something is not right with the url you provided. Please check and try again.")
	sys.exit()

#Reading the payload file from command line if it is provided else using default wordlist
if(wordListFlag==1):
	try:
		payloadsFile = open(wordListPath, 'r')
	except FileNotFoundError:
		print("Error: Could not open/read file:", wordListPath)
		sys.exit()	
else:
	try:
		payloadsFile = open('wordlists/36KCommonDirectoryAndFileNames.txt')
	except OSError:
		print("Default wordlist not found. Please make sure the default wordlists are present in the wordlists directory of inceptionFuzz")
		sys.exit()

print("All looks good. Time to Fuzz....")

print("\nStarting with first level fuzzing\n")

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

requestsSent = 0

payloadCount=len(fuzz)
# Strips the newline character
for payload1 in fuzz:
	count1 += 1
	print("Fuzzing : "+ str(count1)+"/"+str(payloadCount),end='\r')		

	try:
		if(headerCount==0):
			res=requests.get(url+"/"+payload1.strip())		
		elif(headerCount==1):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0]})
		elif(headerCount==2):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1]})
		elif(headerCount==3):
			res=requests.get(url+"/"+payload1.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1],headerList[2]:headerValueList[2]})
	except requests.exceptions.Timeout:
		print("Request Timeout")
	except requests.exceptions.RequestException:
		print("Something went wrong...")
		continue
	except:
		print("Something went wrong...")
		resultFile.close()
		payloadsFile.close()
		sys.exit()

	requestsSent+=1
	if(str(res.status_code)!="404"):
		not404directories.append(payload1)

	if(statusFlag and str(res.status_code) in statusShow):
		result=url+"/"+payload1.strip()+"\t\t"+str(res.status_code)
		resultFile.write(result+"\n")
		print(result)
	elif(statusFlag and str(res.status_code) not in statusShow):
		if(res.status_code==404):
			# Skip
			continue
	elif(statusFlag == 0):
		result=url+"/"+payload1.strip()+"\t\t"+str(res.status_code)
		resultFile.write(result+"\n")
		print(result)	

	
secondLevelFuzzCount=payloadCount*len(not404directories)
print("\n\nFirst level fuzzing is done. \n"+str(len(not404directories))+" URLs were found giving non 404 status code. The tool will now fuzz all these URLs further.\nStarting with second level fuzzing.\n")
resultFile.close() #To save the result of first level fuzz in case of a crash


#Opening a file for writing results of second level fuzzing
resultFile=open(domain+'.txt','a') #Appends at the last



#Second Level Fuzz
for not404 in not404directories:
	secondLevelPayloadFuzz+=1
	for payload2 in fuzz:
		count2 += 1
		print("Fuzzing : "+ str(count2)+"/"+str(secondLevelFuzzCount),end='\r')		

		try:
			if(headerCount==0):
				res=requests.get(url+"/"+not404.strip()+"/"+payload2.strip())
			elif(headerCount==1):
				res=requests.get(url+"/"+not404.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0]})
			elif(headerCount==2):
				res=requests.get(url+"/"+not404.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1]})
			elif(headerCount==3):
				res=requests.get(url+"/"+not404.strip()+"/"+payload2.strip(),headers={headerList[0]:headerValueList[0],headerList[1]:headerValueList[1],headerList[2]:headerValueList[2]})
		except requests.exceptions.Timeout:
			print("Request Timeout")
		except requests.exceptions.RequestException:
			print("Something went wrong...")
			continue
		except:
			print("Something went wrong...")
			resultFile.close()
			payloadsFile.close()
			sys.exit()	

		requestsSent+=1	
				
		if(statusFlag and str(res.status_code) in statusShow):
			result=url+"/"+not404.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
			resultFile.write(result+"\n")
			print(result)
		elif(statusFlag == 0):
			result=url+"/"+not404.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
			resultFile.write(result+"\n")
			print(result)

	print("Done fuzzing for "+str(secondLevelPayloadFuzz)+" of "+str(secondLevelFuzzCount)+" non 404 directories.")		

				
resultFile.close()
payloadsFile.close()


print("\n\nReached the end of payload file. Total Requests Sent:"+str(requestsSent)+"\nBye!!\n")

