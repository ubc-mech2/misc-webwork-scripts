#Description:
#Creates a .tar.gz archive of .pg .png and .pdf files in the current directory
#and names the tarball the current folder name

#How to use:
#Drop this .py file in a directory where the problem files are stored
#Run this script.
#Tarball will be created in the same directory as the problems

import os
import tarfile

current_dir = os.path.basename(os.getcwd())

with tarfile.open(current_dir+'.tar.gz', 'w:gz') as archive:
    archive.format = tarfile.GNU_FORMAT
    for i in os.listdir():
        if i.endswith('.pg') or i.endswith('.png') or i.endswith('.pdf'):
            archive.add(i)

