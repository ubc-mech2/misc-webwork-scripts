import os
import re
from dateparser import parse 

cwd = os.getcwd(); #current working directory
directory = os.listdir(os.getcwd());
fileList = list();

for filename in directory:
    if (filename.endswith(".def")):
        fileList.append(filename);

print("{} .def files found.".format(len(fileList)));

HWDates = open('HWDates.csv','w')
HWDates.write('Set,OpenDate,CloseDate,NumOfProblems\n')

problemAttributes = open('ProblemAttributes.csv','w')
problemAttributes.write('Set,ProblemNumber,FileName,MaxAttempts\n')

for file in fileList:
	f = open(file,'r')
	content = f.read()
	setName = file[3:-4]

	openDate = re.findall('openDate\s*?=\s*?([0-9].*?[ap]m)',content)
	closeDate = re.findall('dueDate\s*?=\s*?([0-9].*?[ap]m)',content)

	matches = re.findall(r"(problem_start.*?problem_end)",content,re.DOTALL)
	
	for match in matches:
		problemNumber = re.findall("problem_id\s*?=\s*?([^\s]*?)$",match,re.MULTILINE)
		problemFileName = re.findall("source_file\s*?=.*?([^\/]*?)\.p[gl]$",match,re.MULTILINE)
		problemMaxAttempts = re.findall("max_attempts\s*?=\s*?([^\s]*?)$",match,re.MULTILINE)
		problemAttributes.write(setName+","+problemNumber[0]+","+problemFileName[0]+","+problemMaxAttempts[0]+"\n")


	try:
		openDate = str(parse(openDate[0]))
		closeDate = str(parse(closeDate[0]))
		HWDates.write(setName+","+openDate+","+closeDate+','+str(len(matches))+"\n")
	except Exception as e:
		print(e)
		print(file)
	f.close()

HWDates.close()
problemAttributes.close()