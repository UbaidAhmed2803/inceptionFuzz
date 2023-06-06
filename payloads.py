from pathlib import Path
from colorama import Fore
from colorama import Style
import sys
import sharedData



#Reading the payload file from command line if it is provided else using default wordlist
def read():
	
	try:
		payloadsFile = open(sharedData.wordlistPath, 'r')
	except FileNotFoundError:
		print(f"{Fore.RED}Error: Could not open/read file: {Fore.GREEN}", sharedData.wordListPath)
		print(f"{Style.RESET_ALL}")
		sys.exit()

	sharedData.payloadList = payloadsFile.readlines()
	


def getCount():
	return len(sharedData.payloadList)

def getStatusFlag():
	return sharedData.statusFlag

def getWordListFlag():
	print(sharedData.wordlistFlag)
	return sharedData.wordlistFlag

# def setPayloadList()