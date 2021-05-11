#Description:
#Adds the line "TEXT(beginproblem());" to .pg files that lack it in a directory.
#The line will be added after the 'loadMacros' section in a .pg file.
#Files that have been processed are added to a folder in the directory.
#The folder's name can be changed by changing the variable 'folderName' below.

#How to use:
#Drop this .py file in a directory where .pg files have to be updated with the line "TEXT(beginproblem());".
#Run this script.
#Collect the updated .pg files in a newly created folder.

import os
import re
import shutil

folderName = "newPGs"

#directory for converted files
if not os.path.exists(folderName): 
    os.makedirs(folderName)
else:
	shutil.rmtree(folderName) #remove old directory
	os.makedirs(folderName)

cwd = os.getcwd(); 
directory = os.listdir(os.getcwd());
fileList = list();

for filename in directory:
    if (filename.endswith(".pg")):
        fileList.append(filename);

print("{} .pg files found.".format(len(fileList)));

for file in fileList:
	f = open(file,"r", encoding="utf-8")

	try:
		content = f.read()

		matchBP = re.findall(r'TEXT\(beginproblem\(\)\);',content,re.IGNORECASE)

		if len(matchBP) == 0 or matchBP is None:
			matchLM = re.findall(r'loadMacros\(.*?\);', content, re.DOTALL)

			index = content.find(matchLM[0]) + len(matchLM[0])

			content = content[:index] + '\n\nTEXT(beginproblem());' + content[index:]

			newPG = open(folderName + "\\" + file, "w", encoding='utf-8')
			newPG.write(content)
			newPG.close()
			print('Completed: ', file)
		else:
			print('Checked: ', file)

	except Exception as e:
		newPG.close()	#close file after error so it can be modified
		print('Failed: ',file,'\n Error: ', e)
		pass

	f.close()

#input()
