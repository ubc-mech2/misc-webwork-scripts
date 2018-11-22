#Description:
#Lists the files with a specified extention in a directory.
#Somewhat useful for pasting a list of filenames in a spreadsheet

#How to use:
#Drop this .py file in a directory and run it.
#Collect results from a file called filelist.txt

import os

cwd = os.getcwd();
ext = ".pg"

fileList = open("filelist.txt","w")

for file in os.listdir(cwd):
	if file.endswith(ext):
		fileList.write(file.replace(ext,"") + "\n")

fileList.close();