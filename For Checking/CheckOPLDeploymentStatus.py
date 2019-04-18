#Description:
#Used with ListPGtoCSV.py
#Checks if a file in 'problems.csv' (refer to ListPGtoCSV.py) has been deployed in WeBWork's Contrib, Pending and OPL folders.
#Currently configured to only dig up UBC Mech2 problems.
#Writes Yes/No to 'problems.csv'.

#How To Use:
#If you haven't already, clone the official OPL's repo found here: https://github.com/openwebwork/webwork-open-problem-library
#Follow instructions listed on ListPGtoCSV.py until 'problems.csv' has been generated.
#Drop this .py file and 'problems.csv' in the repo's home directory and run the script.
#'problems.csv' should have been updated with their deployment status.

import pandas as pd
import os.path
import os
import numpy as np

cwd = os.getcwd()
filePath = 'UBC'

contribPath = os.path.join(cwd,'Contrib\\'+filePath)
pendingPath = os.path.join(cwd,'Pending\\'+filePath)
oplPath = os.path.join(cwd,'OpenProblemLibrary\\'+filePath)

df = pd.read_csv('problems.csv', index_col=0)
df[['InContrib','InPending','InOPL']] = np.nan
df = df.astype(str) 
problemList = df.index.tolist()

for dirpath, dirname, filenames in os.walk(contribPath):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		if filename in problemList:
			df.at[filename,'InContrib'] = 'Yes'

for dirpath, dirname, filenames in os.walk(pendingPath):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		if filename in problemList:
			df.at[filename,'InPending'] = 'Yes'

for dirpath, dirname, filenames in os.walk(oplPath):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		if filename in problemList:
			df.at[filename,'InOPL'] = 'Yes'

df.loc[df.InContrib!='Yes','InContrib']='No'
df.loc[df.InPending!='Yes','InPending']='No'
df.loc[df.InOPL!='Yes','InOPL']='No'

df.to_csv('problems.csv')