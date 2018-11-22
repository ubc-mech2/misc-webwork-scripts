#Description:
#Used with CheckOPLDeploymentStatus.py
#Looks through every .pg file in all subdirectories under this file and writes them to a .csv.
#Along with its companion scriot, CheckOPLDeploymentStatus.py, this is used for checking if any problem file in a subdirectory has been deployed in the OPL

#How to use:
#Drop this .py file in a desired directory and run it.
#Notice that the file problems.csv has been generated. It should contain every problem scanned by this script.
#Refer to CheckOPLDeploymentStatus.py for further instructions.

import os
import os.path
import pandas as pd

directory = os.getcwd();
fileList = list();

for dirpath, dirname, filenames in os.walk(directory):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		#fileList.append(os.path.join(dirpath, filename));
		fileList.append(filename);

print("{} .pg files found.".format(len(fileList)));

df = pd.DataFrame(index = fileList, columns=['InContrib','InPending','InOPL'])

print(df)

df.to_csv('problems.csv')

input();
