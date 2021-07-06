#Description:
#Adds the block "BEGIN_PGML_SOLUTION" to .pg files that lack it in a directory.
#The line will be added after the 'END_PGML' command in a .pg file.
#Files that have been processed are added to a folder in the directory.
#The folder's name can be changed by changing the variable 'folderName' below.

#How to use:
#Drop this .py file in a directory where .pg files need the solution section added.
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

		matchBP = re.findall(r'BEGIN_PGML_SOLUTION',content,re.IGNORECASE)

		if len(matchBP) == 0 or matchBP is None:
			matchLM = re.findall(r'END_PGML', content, re.DOTALL)

			index = content.find(matchLM[0]) + len(matchLM[0])

			content = content[:index] + '\n\n##############################################################' + '\n\nBEGIN_PGML_SOLUTION' + '\n\n[@ image( "' + os.path.splitext(file)[0] + '.pdf", width=>[0], height=>[0]) @]*' + '\n\nEND_PGML_SOLUTION' + '\n\n##############################################################' + content[index:]

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