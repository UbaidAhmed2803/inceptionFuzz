import sys
import argparse
import sharedData
import requests
import math
from colorama import Fore
from colorama import Style


def getArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument("--url", help="This is the url which will be fuzzed. Make sure to provide the complete URL. For eg: https://example.com or https://example.com/admin")
	parser.add_argument("--headers", nargs='*',help="These are the headers that will be used in the request sent to the target URL. For eg: X-Forwarded-For:127.0.0.1")
	parser.add_argument("--status", help="These are the HTTP Status codes. Only the result for those requests will be shown to you whose status codes matches with the one provided by you. For eg: 200,301,302")
	parser.add_argument("--wordlist", help="This is the wordlists which will be used for fuzzing. If no wordlist is provided then the default wordlist of 36K payloads will be used.")
	parser.add_argument("--level", type=int, help="""The level of fuzzing you want to go. Default is level 1. Maximum allowed values is 5.
	\n--level 1: will do the fuzzing for single possition.\nhttps://example.com/FUZZ
	\n--level 2: After fuzzing for level 1, all the non 404 directories will be saved and those directories will further be used for fuzzing for level 2. For eg:\nhttps://example.com/FUZZ/FUZZ\n\n
	IMPORTANT: Be very cautious if you choose level 2 as not only it will take a lot of time but will also generate huge amount of traffic.""")
	args=parser.parse_args()
	url=args.url
	level=args.level
	statusShow=args.status
	wordlist=args.wordlist
	headers=args.headers
	
	if(url != None):
		sharedData.url = args.url.strip()
		if(validateUrl(url)):
			sharedData.url=url
	else:
		print(f"{Fore.RED}No URL Provided.")
		while(sharedData.urlFlag == False):
			url_input=input(f"Please provide a URL to scan: {Style.RESET_ALL}")
			if(url_input != ""):
				sharedData.urlFlag = True
		sharedData.url = url_input.strip()
	print(f"{Fore.BLUE}Target URL: {Fore.GREEN}"+str(sharedData.url)+f"{Style.RESET_ALL}")
	
	if(level!=None):
		sharedData.level=level

	if(statusShow!=None):
		sharedData.statusShow.append(statusShow)

	if(wordlist!=None):
		sharedData.wordlistPath=wordlist


	if(headers!=None):
		sharedData.headers=headers
		getHeaderFromParams()


			
def validateUrl(url):
	print(f"{Fore.BLUE}Performing few checks before fuzzing.......\n{Style.RESET_ALL}")
	try:
		requests.get(url)
	except:
		print(f"{Fore.RED}Error: Something is not right with the url you provided. Please check and try again.{Style.RESET_ALL}")
		sys.exit()

#Each header and its value is being saved as single List item
def getHeaderFromParams():
	for headerSplit in sharedData.headers:
		try:
			sharedData.headerList.append(headerSplit.split(":",1)[0])
			sharedData.headerValueList.append(headerSplit.split(":",1)[1])
		except:
			print(f"\n{Fore.RED}Error: Please check the parameters. Something seems to be wrong with them.{Style.RESET_ALL}")
			sys.exit()
	
	headerCount = len(sharedData.headerList)

	if(sharedData.headers):
		print(f"{Fore.BLUE}Headers: {Fore.GREEN}"+str(sharedData.headers)+f"{Style.RESET_ALL}")

	if(sharedData.wordlistPath):
		print(f"{Fore.BLUE}Wordlist: {Fore.GREEN}"+str(sharedData.wordlistPath)+f"{Style.RESET_ALL}")

def validateParams(args):
	for items in args:
		print(items)




		







# def getParamValues():
