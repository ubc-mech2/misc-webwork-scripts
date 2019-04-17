from dateparser import parse 
import re
import codecs
from sys import stdout

print("Reading log file...")
logFile = codecs.open("answer_log", "r", "utf-8")
log = logFile.readlines()
logFile.close()
print(str(len(log))+" entries found.")

csvFile = open("WWLogRaw.csv","w")

numEntries = 0

csvFile.write("Date,Student,Set,ProblemNumber,Score\n")

for logEntry in log:
	numEntries+=1
	entryData = re.findall('\[(.*?)\]\s\|(\w*?)\|(.*?)\|([0-9]*?)\|([0-9]*?)\s',logEntry)
	try:
		date, student, set, number, correct = entryData[0]
		date = str(parse(date))
		score = str(correct.count("1")/len(correct))
		csvFile.write(date + "," + student + "," + set + "," + number + "," + score + "\n")
	except:
		print("Error parsing line "+str(numEntries)+": " + logEntry)
	if numEntries%100 == 0:
		print(str(numEntries) +" log entries processed.", end = "\r")

print("\nDone")

input()
csvFile.close()