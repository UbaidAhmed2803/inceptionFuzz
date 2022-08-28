# Python code to fuzz a curl request
import requests
import sys
import re
from urllib.parse import urlparse
import pyfiglet
import time
import os
from pathlib import Path
from colorama import Fore
from colorama import Style
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--url", help="This is the url which will be fuzzed. Make sure to provide the complete URL. For eg: https://example.com or https://example.com/admin")
parser.add_argument("--headers", help="These are the headers that will be used in the request sent to the target URL. For eg: X-Forwarded-For:127.0.0.1")
parser.add_argument("--status", help="These are the HTTP Status codes. Only the result for those requests will be shown to you whose status codes matches with the one provided by you. For eg: 200,301,302")
parser.add_argument("--wordlist", help="This is the wordlists which will be used for fuzzing. If no wordlist is provided then the default wordlist of 36K payloads will be used.")
parser.add_argument("--level", help="""The level of fuzzing you want to go. Default is level 1. Another possible values is 2.
	\n--level 1: will do the fuzzing for single possition.\nhttps://example.com/FUZZ
	\n--level 2: After fuzzing for level 1, all the non 404 directories will be saved and those directories will further be used for fuzzing for level 2. For eg:\nhttps://example.com/FUZZ/FUZZ\n\n
	IMPORTANT: Be very cautious if you choose level 2 as not only it will take a lot of time but will also generate huge amount of traffic.""")
args=parser.parse_args()

print("\n")
result = pyfiglet.figlet_format("inceptionFuzz")
print(result)
print("*********************https://ubaidahmed.com*********************\n")
print("\n")

print(f"{Fore.BLUE}Performing few checks before fuzzing.......\n{Style.RESET_ALL}")

urlFlag = False
headersFlag = False
statusFlag = False
wordListFlag = False
levelFlag = False
level=1

#Reading the domain name provided as command line argument
if(args.url != None):
	urlFlag = True
	url = args.url.strip()
	try:
		test=requests.get(url)
	except:
		print(f"{Fore.RED}Error: Something is not right with the URL ("+url+") you provided. Please check and try again.\nExiting.")
		{Style.RESET_ALL}
		sys.exit()
else:
	print(f"{Fore.RED}No URL Provided.")
	while(urlFlag == False):
		url_input=input(f"Please provide a URL to scan: {Style.RESET_ALL}")
		if(url_input != ""):
			urlFlag = True
	url = url_input.strip()
	try:
		test=requests.get(url)
	except:
		print(f"{Fore.RED}Error: Something is not right with the URL ("+url+") you provided. Please check and try again.\nExiting.")
		{Style.RESET_ALL}
		sys.exit()

if(args.level != None):
	levelFlag = True
	try:
		level= int(args.level.strip())
		if(level != 1):
			print(level)
			raise Exception(f"{Fore.RED}Error: Invalid value for level provided. Only Valid values for --level are 1 and 2.\nExiting.{Style.RESET_ALL}")
			sys.exit()
	except:
		print(f"{Fore.RED}Error: Invalid value for level provided. Only Valid values for --level are 1 and 2.\nExiting.{Style.RESET_ALL}")
		sys.exit()

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
		print(f"{Fore.BLUE}Show Status: {Fore.GREEN}"+str(statusShow)+f"{Style.RESET_ALL}")

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
		print(f"\n{Fore.RED}Error: Please check the parameters. Something seems to be wrong with them.{Style.RESET_ALL}")
		sys.exit()
	
headerCount = len(headerList)

if(headerFlag):
	print(f"{Fore.BLUE}Headers: {Fore.GREEN}"+str(headers)+f"{Style.RESET_ALL}")

if(wordListFlag):
	print(f"{Fore.BLUE}Wordlist: {Fore.GREEN}"+str(wordListPath)+f"{Style.RESET_ALL}")

try:
	requests.get(url)
except:
	print(f"{Fore.RED}Error: Something is not right with the url you provided. Please check and try again.{Style.RESET_ALL}")
	sys.exit()

#Reading the payload file from command line if it is provided else using default wordlist
if(wordListFlag==1):
	try:
		payloadsFile = open(wordListPath, 'r')
	except FileNotFoundError:
		print(f"{Fore.RED}Error: Could not open/read file: {Fore.GREEN}", wordListPath)
		print(f"{Style.RESET_ALL}")
		sys.exit()	
else:
	try:
		payloadsFile = open('wordlists/36KCommonDirectoryAndFileNames.txt')
	except OSError:
		print(f"{Fore.RED}ERROR: Default wordlist not found. Please make sure the default wordlists are present in the wordlists directory of inceptionFuzz{Style.RESET_ALL}")
		sys.exit()

print(f"{Fore.BLUE}All looks good. Time to Fuzz....{Style.RESET_ALL}")

print(f"\n{Fore.BLUE}Starting with first level fuzzing\n{Style.RESET_ALL}")

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

#Creating a directory within Results directory
Path("Results/"+domain).mkdir(parents=True, exist_ok=True)
# directoryPath=os.path.join("Results",domain)
# os.mkdir(directoryPath, exist_ok=True)

#Opening a file for writing results
resultFile=open('Results/'+domain+'/results.txt','a') #Appends at the last

#Opening a file for writing non 404 directories
non404File=open('Results/'+domain+'/non404.txt','a') #Appends at the last

#Opening a file for storing any URL which resulted in error
errorFile=open('Results/'+domain+'/error.txt','a') #Appends at the last

requestsSent = 0 #To keep track of total requests sent

payloadCount=len(fuzz)
# Strips the newline character
for payload1 in fuzz:
	count1 += 1
	print(f"{Fore.BLUE}Fuzzing : "+ str(count1)+"/"+str(payloadCount),end='\r')		
	print(f"{Style.RESET_ALL}",end='\r')
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
		print(f"{Fore.RED}Request Timeout{Style.RESET_ALL}")
		errorFile.write(url+"/"+payload1+" - Request Timeout")
	except requests.exceptions.RequestException:
		print(f"{Fore.RED}Something went wrong...{Style.RESET_ALL}")
		errorFile.write(url+"/"+payload1+" - Exception Occurred")
		continue
	except:
		print(f"{Fore.RED}Something went wrong...{Style.RESET_ALL}")
		non404File.close()
		resultFile.close()
		payloadsFile.close()
		sys.exit()

	requestsSent+=1
	if(str(res.status_code)!="404"): #Storing the urls giving non 404 directories
		not404directories.append(payload1)
		non404File.write(str(res.status_code)+" : "+url+"/"+payload1)

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

non404File.close() #Closing to prevent loss of data if there is a crash during second level fuzzing
resultFile.close() #To save the result of first level fuzz in case of a crash
errorFile.close() 

#Second Level Fuzz only if there is atleast one non 404 directory from first level fuzz
if(len(not404directories)>0 & level == 2):
	secondLevelFuzzCount=payloadCount*len(not404directories)
	print(f"{Fore.BLUE}\n\nFirst level fuzzing is done. \n"+str(len(not404directories))+f" URLs were found giving non 404 status code. The tool will now fuzz all these URLs further.\nStarting with second level fuzzing.\n{Style.RESET_ALL}")

	#Opening a file for writing results of second level fuzzing
	resultFile=open('Results/'+domain+'/results_2ndLevel.txt','a') #Appends at the last

	#Opening a file for writing non 404 directories during
	non404File=open('Results/'+domain+'/non404_2ndLevel.txt','a') #Appends at the last

	#Opening a file for storing any URL which resulted in error
	errorFile=open('Results/'+domain+'/error.txt','a') #Appends at the last

	for not404 in not404directories:
		
		for payload2 in fuzz:
			secondLevelPayloadFuzz+=1
			count2 += 1
			print(f"{Fore.BLUE}Fuzzing : "+ str(count2)+"/"+str(secondLevelFuzzCount),end='\r')
			print(f"{Style.RESET_ALL}",end='\r')		

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
				print(f"{Fore.RED}Request Timeout{Style.RESET_ALL}")
				errorFile.write(url+"/"+payload1+"/"+payload2+" - Request Timeout")
			except requests.exceptions.RequestException:
				print(f"{For.RED}Something went wrong...{Style.RESET_ALL}")
				errorFile.write(url+"/"+payload1+"/"+payload2+" - Exception Occurred")
				continue
			except:
				print(f"{Fore.RED}Something went wrong...{Style.RESET_ALL}")
				resultFile.close()
				payloadsFile.close()
				sys.exit()	

			requestsSent+=1	
			if(str(res.status_code)!="404"):
				non404File.write(url+"/"+not404+"/"+payload2)
					
			if(statusFlag and str(res.status_code) in statusShow):
				result=url+"/"+not404.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
				resultFile.write(result+"\n")
				print(result)
			elif(statusFlag == 0):
				result=url+"/"+not404.strip()+"/"+payload2.strip()+"\t"+str(res.status_code)
				resultFile.write(result+"\n")
				print(result)

	print(f"{Fore.BLUE}Done fuzzing for "+str(secondLevelPayloadFuzz)+" of "+str(secondLevelFuzzCount)+" non 404 directories.")	
	print("\n\nReached the end of payload file. \nTotal Requests Sent:"+str(requestsSent)+"\nResults are saved in Results/"+domain+f" directory.\nBye!!{Style.RESET_ALL}")	

	errorFile.close()
	non404File.close()				
	resultFile.close()
	payloadsFile.close()
else:
	if(level!=2):
		print(f"{Fore.BLUE}\nTotal Requests Sent:"+str(requestsSent)+"\nResults are saved in Results/"+domain+f" directory.\nBye!!{Style.RESET_ALL}")
	else:
		print(f"{Fore.BLUE}\nThere was no non 404 directory found in the first level fuzz. Hence, not going for the second level fuzz.\nTotal Requests Sent:"+str(requestsSent)+"\nResults are saved in Results/"+domain+f" directory.\nBye!!{Style.RESET_ALL}")
		




