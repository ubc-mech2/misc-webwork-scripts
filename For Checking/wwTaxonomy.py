#Description
#Looks through every .pg file in all subdirectories under this file and compiles subject-chapter-section data
#Outputs the result to a .txt file
#Used for scraping the taxonomy of the entire OPL directory, including Contrib and Pending

#How to use:
#If you haven't already, clone the official OPL's repo found here: https://github.com/openwebwork/webwork-open-problem-library
#Drop this .py file in the repo's home directory (or any directory with .pg files in the directory and/or subdirectories).
#Run this script.
#A file called Taxonomy.txt should be generated.

import os
import re

directory = os.getcwd();
fileList = list();

for dirpath, dirname, filenames in os.walk(directory):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		fileList.append(os.path.join(dirpath, filename));

print("{} .pg files found.".format(len(fileList)));

subjects = list();
chapters = dict();
sections = dict();
i=0;

for file in fileList:
	f = open(file,"r");
	
	try:
		content = f.read();

		##subject
		start = content.find("DBsubject(");
		if not (start == -1):
			end = content.find(")",start);

			DBsubject = content[start+len("DBsubject("):end];
			DBsubject = re.sub('[\'\"Â’™ƒ€‚Ãâ‘˜]','',DBsubject);
		else:
			f.close();
			continue;

		##chapter
		start = content.find("DBchapter(");
		if not (start == -1):
			end = content.find(")",start);

			DBchapter = content[start+len("DBchapter("):end];
			DBchapter = re.sub('[\'\"Â’™ƒ€‚Ãâ‘˜]','',DBchapter);
		else:
			f.close();
			continue;

		##section
		start = content.find("DBsection(");
		if not (start == -1):
			end = content.find(")",start);

			DBsection = content[start+len("DBsection("):end];
			DBsection = re.sub('[\'\"Â’™ƒ€‚Ãâ‘˜]','',DBsection);
		else:
			f.close();
			continue;

		if DBsubject not in subjects: 
			subjects.append(DBsubject);
		chapters.update({DBchapter:DBsubject});
		sections.update({DBsection:DBchapter});

		i+=1;
		if(i%1000==0):
			print(i, "files read.")

	except:
		j = 1;

	f.close();

print("Processing headers.");

taxonomy = open("Taxonomy.txt","w")

for subject in subjects:
	taxonomy.write(subject + "\n")
	for chapterKey, chapterValue in chapters.items():
		if (chapterValue == subject):
			taxonomy.write("\t"+chapterKey + "\n");
			for sectionKey, sectionValue in sections.items():
				if (sectionValue == chapterKey):
					taxonomy.write("\t\t"+sectionKey + "\n");

print("Operation complete. Taxonomy.txt has been created.");
taxonomy.close();

input();