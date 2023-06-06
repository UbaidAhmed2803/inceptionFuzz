from pathlib import Path
from colorama import Fore
from colorama import Style
from bs4 import BeautifulSoup
from tabulate import tabulate
import json
import sys
import results
import sharedData
import requests
import payloads
import time
import http.client
import re

requestsSent=0

def start():
	print(f"{Fore.BLUE}All looks good. Time to Fuzz....{Style.RESET_ALL}")

	#Check if the url ends with / and if it does remove /
	last_char=sharedData.url[-1]
	if(last_char=="/"):
		sharedData.url=sharedData.url.rstrip(sharedData.url[-1]) #Setting the value of URL

	sharedData.requestsSent = 0 #To keep track of total requests sent
	
	results.openFiles()

	fuzz(sharedData.level)

	results.closeFiles()

def setNextLevelUrl(baseUrl,fuzzCounter):
	urlToFuzz =baseUrl+"/"+sharedData.not404directories[fuzzCounter].strip()
	
	return urlToFuzz


def requestBlocked():
	sharedData.requestsBlockedCount+=1

def getRequestsBlockedCount():
	return sharedData.requestsBlockedCount

def getHostAndPath(url):
    # Extract the host and path using a regular expression
    pattern = r"https?://([^/]+)(/.*)?"
    match = re.match(pattern, url)
    if match:
        host = match.group(1)
        path = match.group(2) if match.group(2) else "/"
        return host, path

    raise ValueError("Invalid URL format")

def getTitleFromResponse(response_data):
    # Extract the title of the page using a regular expression
    pattern = r"<title>(.*?)</title>"
    match = re.search(pattern, response_data, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def fuzz(level):
	levelCounter = 0
	payloadCounter = 0
	percentage = 0
	fuzzCounter = 0
	urlToFuzz = baseUrl = sharedData.url

	resultTableHeaders=["URL","Status Code","Page Title","Content Length"]
	
	print(f"{resultTableHeaders[0]:{70}} {resultTableHeaders[1]:{30}} {resultTableHeaders[2]:{20}} {resultTableHeaders[3]:{20}}")
	
	while(levelCounter<level):
		for payloadValue in sharedData.payloadList:
			payloadCounter += 1
			
			print(f"{Fore.BLUE}Fuzzing : {payloadCounter} payloads sent {Style.RESET_ALL}",end='\r')		
			
			status_code,appsRunning,contentLength=sendRequest(urlToFuzz,payloadValue)

			fuzzedUrl = urlToFuzz.strip()+"/"+payloadValue.strip()
			if(status_code is not None):
				if(levelCounter!=level):
					if(str(status_code)!="404"): #Storing the urls giving non 404 directories
						if payloadValue not in sharedData.not404directories:
							sharedData.not404directories.append(payloadValue)
						sharedData.non404File.write(str(status_code)+" : "+urlToFuzz+"/"+payloadValue.strip())

					if(sharedData.statusShow and str(status_code) in sharedData.statusShow):
						print(f"{fuzzedUrl:{70}} {str(status_code):{20}} {str(appsRunning):{30}} {str(contentLength):{10}}")
						sharedData.resultFile.write(f"{fuzzedUrl:{70}} {str(status_code):{20}} {str(appsRunning):{30}} {str(contentLength):{10}}")
					elif(sharedData.statusShow and status_code not in sharedData.statusShow):
						if(status_code==404):
							# Skip
							return
					elif(sharedData.statusFlag == 0):
						print(f"{fuzzedUrl:{70}} {str(status_code):{20}} {str(appsRunning):{30}} {str(contentLength):{10}}")
						sharedData.resultFile.write(f"{fuzzedUrl:{70}} {str(status_code):{20}} {str(appsRunning):{30}} {str(contentLength):{10}}")
			else:
				print(fuzzedUrl+" Request Blocked")
						

		
		if(level>1):
			
			if(fuzzCounter<len(sharedData.not404directories)):
				urlToFuzz=setNextLevelUrl(baseUrl,fuzzCounter)		
				fuzzCounter+=1	
			nextLevelFuzzCount=payloads.getCount()*len(sharedData.not404directories)
		
				
			if(fuzzCounter==len(sharedData.not404directories)):
				levelCounter=level


		if(level==1):
			levelCounter+=1


def sendRequest(urlToFuzz,payloadValue):
	maxRetries = 5
	retryDelay = 1
	retryCounter = 0
	result = None
	headers=len(sharedData.headerList)

	host, path = getHostAndPath(urlToFuzz)
	connection = http.client.HTTPSConnection(host)

	#In case request is not fulfilled, attempt will be made 5 times
	while(retryCounter<5):
		try:
			if(headers==0):
				connection.request("GET", path+"/payloadValue")
			elif(headers==1):
				connection.request("GET", path+"/payloadValue", headers={sharedData.headerList[0]:sharedData.headerValueList[0]})
			elif(headers==2):
				connection.request("GET", path+"/payloadValue", headers={sharedData.headerList[0]:sharedData.headerValueList[0],sharedData.headerList[1]:sharedData.headerValueList[1]})
			elif(headers==3):
				connection.request("GET", path+"/payloadValue", headers={sharedData.headerList[0]:sharedData.headerValueList[0],sharedData.headerList[1]:sharedData.headerValueList[1],sharedData.headerList[2]:sharedData.headerValueList[2]})
		except requests.exceptions.Timeout as ex:
			print(f"{Fore.RED}Request Timeout{Style.RESET_ALL} \n{ex}")
			sharedData.errorFile.write(urlToFuzz+"/"+payloadValue.strip()+" - Request Timeout")
		except requests.exceptions.RequestException as ex:
			print(f"{Fore.RED}Failed to resolve...{urlToFuzz.strip()}/{payloadValue.strip()}{Style.RESET_ALL} \n{ex}")
			time.sleep(5)
			response=requests.get(urlToFuzz)
			print(urlToFuzz+str(response.status_code))
			#Think about Returning Failed to resolve and printing the same as result in output. Test with other urls
			sharedData.errorFile.write(urlToFuzz+"/"+payloadValue.strip()+" - Exception Occurred")
		except http.client.HTTPException as e:
			print("An HTTP exception occurred:", e)
		except Exception as ex:
			print(f"Caught an unhandled exception: {type(ex).__name__}: {ex}")
			requestBlocked()

		response = connection.getresponse()
		response_data = response.read().decode('utf-8')
		response_code = response.code
		title = getTitleFromResponse(response_data)
		contentLength=len(response_data)

		if(response is not None):
			return response_code,title,contentLength
		elif(retryCounter==5):
			if(response is None):
				time.sleep(10)
				#if total 50 requests get blocked then quitting the scan
				if(getRequestsBlockedCount()==50):
					# print(getRequestsBlockedCount())
					print("The host is blocking our requests. This could be due to a firewall. Please try to run the scan again using one of the following \n\t\t --headers  X-Forwarded-For:127.0.0.1\n Exiting Now")
					sys.exit()	
				print(urlToFuzz+"/"+payloadValue+ " Max Retries exceeded without a successful response.")
				return response_code,title,contentLength
		
		retryCounter+=1
		

		connection.close()

	return response_code,title,contentLength





