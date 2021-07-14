#Description:
#Replaces the dots in .pg .png .pdf files with dashes in a directory.
#The lines referencing solution and images will be changed as well in a .pg file to reflect the new file names.
#Files that have been processed are added to a folder in the directory.
#The folder's name can be changed by changing the variable 'folderName' below.

#How to use:
#Drop this .py file in a directory where .pg .png .pdf files need the name changed.
#Run this script.
#Collect the updated files in a newly created folder.

import os
import re
import shutil

folderName = "newFiles"

#directory for converted files
if not os.path.exists(folderName): 
    os.makedirs(folderName)
else:
	shutil.rmtree(folderName) #remove old directory
	os.makedirs(folderName)

cwd = os.getcwd(); 
directory = os.listdir(os.getcwd());
fileList = list();
pngList = list();
pdfList = list();

for filename in directory:
    if (filename.endswith(".pg")):
        fileList.append(filename);

for filename in directory:
    if (filename.endswith(".png")):
        pngList.append(filename);

for filename in directory:
    if (filename.endswith(".pdf")):
        pdfList.append(filename);

print("{} .pg files found.".format(len(fileList)));
print("{} .png files found.".format(len(pngList)));
print("{} .pdf files found.".format(len(pdfList)));

for file in fileList:

	f = open(file,"r", encoding="utf-8")

	try:
		content = f.read()

		content = content.replace(os.path.splitext(file)[0], os.path.splitext(file)[0].replace(".","-"))

		filechangedname = os.path.splitext(file)[0].replace(".","-") + ".pg"

		newPG = open(folderName + "\\" + filechangedname, "w", encoding='utf-8')
		newPG.write(content)
		newPG.close()
		print('Completed: ', file)

	except Exception as e:
		newPG.close()	#close file after error so it can be modified
		print('Failed: ',file,'\n Error: ', e)
		pass

	f.close()

for file in pngList:

	filechangedname = os.path.splitext(file)[0].replace(".","-") + ".png"

	shutil.copy(file, folderName + "/" + filechangedname)

	f.close()

for file in pdfList:

	filechangedname = os.path.splitext(file)[0].replace(".","-") + ".pdf"

	shutil.copy(file, folderName + "/" + filechangedname)

	f.close()

#input()