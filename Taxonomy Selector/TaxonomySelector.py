#Description
#Used to avoid typing/pasting a problem's subject-chapter-section designations one by one in a .pg file's header
#Generates an .html file that copies the taxonomy of a WeBWork problem to the clipboard on click.
#The text copied to clipboard are in a format ready for pasting in a .pg file's ## DBSubject, ## DBChapter, ## DBSeection header.
#Must have the file 'Taxonomy2' from official OPL's repo, found here: https://github.com/openwebwork/webwork-open-problem-library

#How to Use:
#Drop this .py file in the same directory as the file, 'Taxonomy2' and run it.
#Notice that an .html file called TaxonomySelector.html has been generated.
#Make sure that clipboard.js, collapse.js, selector.js, and selector.css is in the same folder as TaxonomySelector.html
#View the webpage by dragging it to a web browser.
#Untested on browsers besides Chrome or Firefox. 

import re

def HTMLStartText():
	text = ""
	text+="<!DOCTYPE html>\n<html>\n<head>\n"
	text+="\t<title></title>\n"
	text+="\t<script src=\"clipboard.js\"></script>\n"
	text+="\t<link rel=\"stylesheet\" type=\"text/css\" href=\"selector.css\">\n"
	text+="</head>\n<body>\n\n\t<div>\n\n"
	return text

def HTMLEndText():
	text=""
	text+= "\n\t</div>\n\n\t<script src=\"selector.js\"></script>\n\n"
	text+= "\t<script src=\"collapse.js\"></script>\n\n"
	text+="</body>\n</html>"
	return text


with open('Taxonomy2') as f:
    lines = f.readlines()

subjectChapter = dict()
subjBlocks = [""]

taxonomy=open("TaxonomySelector.html","w");

noTabs = 0;
blocks = 0;

for line in lines:

	line = re.sub("<<<.*$","",line)

	numTabs = line.count("\t")
	
	if numTabs == 0:
		noTabs+=1

	if (noTabs>=1) and noTabs != 0:
		subjBlocks.append("")
		blocks+=1;
		noTabs = 0

	subjBlocks[blocks]+=line

for subjBlock in subjBlocks:
	lines = subjBlock.splitlines()

	if len(lines)!=0:
		subject = lines.pop(0)
		subjectChapter[subject] = dict()

		for line in lines:
			if line.count("\t")==2:
				section = line.replace("\t","")
				subjectChapter[subject][chapter].append(section)
			else:
				chapter = line.replace("\t","")
				subjectChapter[subject][chapter] = list()

'''	
debug = open("debug.txt","w")
for subject, chapterSection in subjectChapter.items():
	debug.write(subject + "\n")
	for chapter, sectionList in chapterSection.items():
		debug.write("\t"+chapter+"\n")
		for section in sectionList:
			debug.write("\t\t"+section+"\n")
debug.close();
'''		


taxonomy.write(HTMLStartText())

for subject, chapterSection in subjectChapter.items():
	taxonomy.write("\t\t<button class=\"collapsible\">" + subject.strip() + "</button>\n\t\t\t<div class=\"content\">\n")
	for chapter, sectionList in chapterSection.items():
		taxonomy.write("\t\t\t<div class=\"chapter btn\" data-clipboard-text=\"## DBsubject(" + subject.strip() + ")&#10;## DBchapter(" + chapter.strip() +")\">" + chapter.strip() + "</div>\n")
		for section in sectionList:
			taxonomy.write("\t\t\t\t<div class=\"section btn\" data-clipboard-text=\"## DBsubject(" + subject.strip() + ")&#10;## DBchapter(" + chapter.strip() +")&#10;## DBsection(" + section.strip() + ")\">" + section.strip() + "</div>\n")
	taxonomy.write("\t\t</div>\n\n")

taxonomy.write(HTMLEndText())

taxonomy.close();
f.close();


input();


