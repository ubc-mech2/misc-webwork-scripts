#Description:
#Can either export everything in a Desire2Learn question database into a single folder, or into multiple folders named after the problem's section (just change the singleFolder variable from True to False of vice versa).
#Requires the contents of the D2L zip file to work.
#To convert files, just run this script. Keep in mind that it can fail without warning.
#An example zip file is included in this folder too. Unzip the contents to see the conversion script in action.

import re
import codecs
import xml.etree.ElementTree as ET
import os
import shutil
import random
from shutil import copyfile

singleFolder = True
questionDB = "questiondb.xml"
folderName = "Exported";

def ReplaceVariablesFormula(text):
	matches = re.findall("\{(.*?)\}", text) #get D2L variables enclosed in {curly braces}

	for match in matches: #convert every variable formatted in D2L to WebWork pgml formulas
		toReplace = "{" + match + "}"
		replacement = "$" + match 

		text = text.replace(toReplace, replacement)

	text =  text.replace("^","**")
	text = text.replace("sqr","sqrt")

	return text

def ReplaceVariablesText(text):
	matches = re.findall("\{(.*?)\}", text) #get D2L variables enclosed in {curly braces}

	for match in matches: #convert every variable formatted in D2L to WebWork pgml text
		toReplace = "{" + match + "}"
		replacement = "[$" + match + "]"

		text = text.replace(toReplace, replacement)

	return text

def MathML2Latex(text, mode = "pgml"):

	annotation = re.findall('(?<=<annotation encoding="latex">)(.*?)(?=<\/annotation>)',text)[0]
	annotation = annotation.replace("&quot;","\"") #just in case
	latex = re.findall('(?<=math":")(.*?)(?=")',annotation)[0]

	if mode == "pgml":
		latex = "[`" + latex + "`]"
	else:
		latex = "\\(" + latex + "\\)"

	return latex	

def ReplaceImageCode(text, mode = "pgml"): 
	text = text.replace("%20"," ") #replace all %20's with spaces

	while not (text.find("<img")==-1):#do this while there are image tags

		toReplace = re.findall('<img.*?\/>', text)[0] #image tag in xml to be replaced with pgml equivalent

		imageName = re.findall('(?<=src)\=\"(.*?)\"', toReplace)[0] #gets image reference in src=""
		
		width = re.findall('(?<=width)\=\"(.*?)\"', toReplace) #gets image width in width=""
		#set width to 0 if it's not specified
		if (len(width)==0):
			width = 500
		else:
			width = width[0]

		height = re.findall('(?<=height)\=\"(.*?)\"', toReplace) #gets image height in height=""
		#set height to 0 if it's not specified
		if (len(height)==0):
			height = 500
		else:
			height = height[0]

		if mode == "pgml":
			replacement = "[@ image(\'" + imageName + "\', width=>" + str(width) + ", height=>" + str(height) + ") @]*" #pgml equivalent
		else: 
			replacement = "\\{ image(\'" + imageName + "\', width=>" + str(width) + ", height=>" + str(height) + ") \\}" #pg equivalent

		text = text.replace(toReplace,replacement)

	return text

def ReplaceParagraphTags(text): #replaces paragraph tags with line breaks
	num = text.count("</p>") - 1;

	text = text.replace("</p>","\n\n",num);
	text = text.replace("</p>","");
	matches = re.findall('(?<=<p)(.*?)(?=\>)',text)
	for match in matches:
		text = text.replace("<p"+match+">","")

	return text

def ReplaceMiscText(text, mode = "pgml"):

	#convert html url spaces
	text = text.replace("%20", " ") 

	#remove line breaks
	text = text.replace("\n","")

	#replace non breaking space character
	text = text.replace("&nbsp;"," ")

	#replace quotes
	text = text.replace("&quot;","\"")
	
	#replace ampersand
	text = text.replace("&amp;","&")

	#replace unicode characters
	matches = re.findall('(?<=\&)(.*?)(?=;)',text)
	for match in matches:
		if not (match=="gt" or match == "lt"):
			if mode == "pgml":
				text=text.replace('&' + match + ';','[`\\' + match + '`]',1)
			else:
				text=text.replace('&' + match + ';','\\(\\' + match + '\\)',1)

	text = text.replace("&gt;",">")
	text = text.replace("&lt;","<")
	text = text.replace("\\micro", "\\mu")
	text = text.replace("\\ordm", "\\^circ{}")

	#remove spans
	text = text.replace("</span>","")
	matches = re.findall('(?<=<span)(.*?)(?=\>)',text)
	for match in matches:
		text = text.replace("<span"+match+">","")

	if mode=="pgml": #pgml markdown
		boldStart = "*"
		boldEnd = "*"
		italicsStart = "_"
		italicsEnd = "_"
	else: #pg markdown
		boldStart = "$BBOLD "
		boldEnd = "$EBOLD "
		italicsStart = "$BITALIC "
		italicsEnd = "EITALIC "

	#add boldface to <strong>, <u>, and <b> tags
	text = text.replace("<strong>",boldStart)
	text = text.replace("</strong>",boldEnd)
	text = text.replace("<b>",boldStart)
	text = text.replace("</b>",boldEnd)
	text = text.replace("<u>",boldStart)
	text = text.replace("</u>",boldEnd)

	#add italics to <i> tag
	text = text.replace("<i>",italicsStart)
	text = text.replace("</i>",italicsEnd)

	#remove things that look like links
	text = text.replace("</a>","")
	matches = re.findall('(?<=<a)(.*?)(?=\>)',text)
	for match in matches:
		text = text.replace("<a"+match+">","")

	#remove <ul>, <ol>, <li> tags and add respective line breaks
	text = text.replace("<ol>","")
	text = text.replace("</ol>","")
	text = text.replace("</ul>","")
	text = text.replace("<ul>","")
	text = text.replace("</li>","\n\n")
	text = text.replace("<li>","")

	#remove br tags and add line breaks
	text = re.sub('<br*?[\s]*?\/>',"\n\n",text)

	return text

def ReplaceSubSuperScripts(text):
	
	#convert subscripts and superscripts
	text = text.replace("<sub>","_{") 
	text = text.replace("</sub>","}")
	text = text.replace("<sup>","^{")
	text = text.replace("</sup>","}")

	return text

def ProcessText(text, mode = "pgml"):

	#remove line breaks for easier processing
	text = text.replace("\n","")


	mathTags = re.findall('<math.*<\/math>',text)
	text = ReplaceVariablesText(text) #replaces variables surrounded by {} in D2L to [$] used in WebWork 

	for mTag in mathTags: #fix the Latex formatting errors caused by ReplaceVariablesText() because Latex also uses {}
		text = text.replace(ReplaceVariablesText(mTag),MathML2Latex(mTag,mode))

	text = ReplaceSubSuperScripts(text)
	text = ReplaceMiscText(text, mode)
	text = ReplaceParagraphTags(text)
	text = ReplaceImageCode(text, mode)

	#find braces that surround one or more whitespace characters and remove them for easier processing
	text = re.sub('(?<={)\s*?(?=})',"",text)

	#remove stuff like W_{2 } or V^{ 2}. random whitespaces in between {} tends to confuse the regex 
	matches = re.findall('{[\s]*?\w[\s]*?}', text)
	for match in matches:
		replacement = match.replace(" ", "")
		text = text.replace(match, replacement,1) #only replace 1st instance to make sure the text doesnt get screwed up

	#correct stuff like "a^{2}is". The regex below will include the words next to a closing bracket in Latex markdown if it's not separated by whitespace
	offset = 0
	for closeBrace in re.finditer('}(?=\w)', text):
		location = closeBrace.span()
		text = text[:location[0]+offset+1] + " " + text[location[0]+offset+1:]
		offset+=1

	#add Latex markdown to strings surrounded by {} so WebWork can render them properly
	regex = re.compile(r'(?<=[?.,<>`\]\[}(\s])[^\s\[\]\`\}?]*?\{+[^\[\]\`]*?\}+[^\s\[\]\`\{?]*?(?=[\s,.<>\[\]?`){])')
	offset = 0 
	for toBeLatexed in re.finditer(regex,text): #get positions of stuff surrounded by {}

		isNested = False

		locNew = toBeLatexed.span()
		#have to repeat this every loop because locations change every time Latex markdown is added (assumes no nested markdown currently exists)
		for existingMarkdown in re.finditer('[\\\[][\`\(].*?[\`\\][\]\)]',text): #finds [`whatever`] or \(whatever\)

			locExisting = existingMarkdown.span()
			#check if Latex markdown is about to be placed inside existing Latex markdown (to avoid nested markdowns)
			for i in range(0,2):
				if ((locNew[i]+offset>=locExisting[0]) and (locNew[i]+offset<=locExisting[1])):
					isNested = True
					break

			if (isNested):
				break

		#if the string about to be marked down is confirmed to be not nested, add markdown
		notYetLatex = text[locNew[0]+offset:locNew[1]+offset]
		if (not isNested) and notYetLatex.find("image") == -1:
			if mode == "pgml":
				text = text[:locNew[0]+offset] + "[`" + text[locNew[0]+offset:locNew[1]+offset] + "`]" + text[locNew[1]+offset:]
			else:
				text = text[:locNew[0]+offset] + "\\(" + text[locNew[0]+offset:locNew[1]+offset] + "\\)" + text[locNew[1]+offset:]

			offset+=4;

	offset = 0
	for toBeLatexed in re.finditer('[\.\d]+[\"\'](?=[\s\W]|$)',text): #get numbers next to " (inch) or ' (foot)

		isNested = False

		locNew = toBeLatexed.span()
		#have to repeat this every loop because locations change every time Latex markdown is added (assumes no nested markdown currently exists)
		for existingMarkdown in re.finditer('[\\\[][\`\(].*?[\`\\][\]\)]',text): #finds [`whatever`] or \(whatever\)

			locExisting = existingMarkdown.span()
			#check if Latex markdown is about to be placed inside existing Latex markdown (to avoid nested markdowns)
			for i in range(0,2):
				if ((locNew[i]+offset>=locExisting[0]) and (locNew[i]+offset<=locExisting[1])):
					isNested = True
					break

			if (isNested):
				break

		notYetLatex = text[locNew[0]+offset:locNew[1]+offset]
		if (not isNested) and notYetLatex.find("image") == -1:
		#if the string about to be marked down is confirmed to be not nested, add markdown
			if mode == "pgml":
				text = text[:locNew[0]+offset] + "[`" + text[locNew[0]+offset:locNew[1]+offset] + "`]" + text[locNew[1]+offset:]
			else:
				text = text[:locNew[0]+offset] + "\\(" + text[locNew[0]+offset:locNew[1]+offset] + "\\)" + text[locNew[1]+offset:]

			offset+=4;

	#check if the first word needs Latex markdown
	#the above regex never matches the first word
	if text.find(" ")!=-1:
		firstWord = text[0:text.find(" ")]
		if (firstWord.find("\\(") == -1 and firstWord.find("\\)") == -1 and firstWord.find("[`") == -1 and firstWord.find("`]") == -1):
			if ((re.search("[^\s\[\]\`\}]*?\{+[^\[\]\`]*?\}+[^\s\[\]\`\{]*?", firstWord) is not None) or (re.search('[\d\.]+[\"\']',firstWord) is not None)):
				if mode == "pgml":
					text = text.replace(firstWord, '[`'+firstWord + '`]',1)
				else:
					text = text.replace(firstWord, '\\('+firstWord + '\\)',1)

	return text

def GetProblemTextArithmetic(item):
	#params: xml.etree.ElementTree.Element object
	#returns: str

	text = ""

	for flow in item.iter('flow'):
		#get problem text
		for mattext in flow.iter('mattext'):
			text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ProcessText(text)

	return text
	
def GetVariablesArithmetic(item):

	text = ""

	varName = list();
	varMinVal = list();
	varMaxVal = list();
	varStep = list();
	varCount = 0

	for variable in item.iter('variable'):

		varName.append(" "); #just in case the get/find methods return null values
		varName[varCount] = variable.get('name')

		varMinVal.append(" ");
		varMinVal[varCount] = variable.find('minvalue').text
		if (variable.find('minvalue_exp') is not None):
			varMinVal[varCount] += "**("+variable.find('minvalue_exp').text+")"

		varMaxVal.append(" ");
		varMaxVal[varCount] = variable.find('maxvalue').text
		if (variable.find('maxvalue_exp') is not None):
			varMaxVal[varCount] += "**("+variable.find('maxvalue_exp').text+")"

		varStep.append(" ");
		if (variable.find('step').text is not None):
			varStep[varCount] = variable.find('step').text
			if (variable.find('step_exp') is not None):
				varStep[varCount] += "**("+variable.find('step_exp').text+")"
		else:#default
			varStep[varCount] = str(1);

		varCount+=1;

	if len(varName)!=0 :
		for i in range(0,len(varName)):
			text+="$"+varName[i]+" = random(" + varMinVal[i] + "," + varMaxVal[i] + "," + varStep[i] + ");\n"

	return text

def GetAnswersArithmetic(item):
#assumes no multi-answer questions

	for resprocessing in item.iter('resprocessing'):

		for formula in resprocessing.iter('formula'):
			formula = formula.text;
			formula = ReplaceVariablesFormula(formula)
			break

		for tolerance in resprocessing.iter('tolerance'):
			tol = tolerance.text;
			toltype = tolerance.get('type')
			break

		break

		

	return formula, tol, toltype

def GetProblemTextTrueFalse(item):
	
	text = ""
	
	#go through the tree and find the main problem text. 
	#implementation's a bit messy, but it prevents the algorithm from grabbing the options
	for flow in item.iter('flow'):
		for child in flow:
			if child.tag == "material":
				for mattext in child.iter('mattext'):
					text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ProcessText(text)

	return text

def GetAnswersTrueFalse(item):

	TFdict = dict()
	answer = True;

	for flow in item.iter('flow'):
		for response in flow.iter('response_lid'):
			for label in response.iter('response_label'):
				id = label.get('ident')
				for mattext in label.iter('mattext'):
					trueOrFalse = mattext.text
				TFdict.update({id:trueOrFalse})

	for resprocessing in item.iter('resprocessing'):
		for respcondition in resprocessing.iter('respcondition'):
			for respID in respcondition.iter('varequal'):
				id = respID.text
				break
			for isCorrect in respcondition.iter('setvar'):
				if float(isCorrect.text) == 0:
					#this particular response ID is wrong
					correct = False;
				else:
					#if it's right
					correct = True;
				break
			break
		break

	#This doesnt seem to make sense, but it worked perfectly during testing
	if TFdict[id]=="True" and correct:
		answer = True
	elif TFdict[id]=="False" and correct:
		answer = False		
	elif TFdict[id]=="True" and not correct:
		answer = False		
	elif TFdict[id]=="False" and not correct:
		answer = True

	return answer

def GetProblemTextMultipleChoice(item):
		
	text = ""
	
	#go through the tree and find the main problem text. 
	#implementation's a bit messy, but it prevents the algorithm from grabbing the options
	for flow in item.iter('flow'):
		for child in flow:
			if child.tag == "material":
				for mattext in child.iter('mattext'):
					text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ProcessText(text)

	return text

def GetChoicesMultipleChoice(item):

	choicesDict = dict()
	choices = list()
	correctID = 0

	for flow in item.iter('flow'):
		for response in flow.iter('response_lid'):
			for label in response.iter('response_label'):
				id = label.get('ident')
				for mattext in label.iter('mattext'):
					choiceText = mattext.text
					choiceText = ProcessText(choiceText, "pg")
				choicesDict.update({id:choiceText})

	for resprocessing in item.iter('resprocessing'):
		for respcondition in resprocessing.iter('respcondition'):
			for respID in respcondition.iter('varequal'):
				id = respID.text
				break
			for value in respcondition.iter('setvar'):
				if float(value.text)==100:
					correctID = id
					break

	#just in case no correct ID has been identified
	try:
		correctChoice = choicesDict[correctID]
	except:
		for k in choicesDict:
			correctChoice = choicesDict[k]
			break

	#pass choices to list after the correct answer has been selected
	for k, v in choicesDict.items():
		choices.append(v)

	return choices,correctChoice

def GetProblemTextMultiSelect(item):
		
	text = ""
	
	#go through the tree and find the main problem text. 
	#implementation's a bit messy, but it prevents the algorithm from grabbing the options
	for flow in item.iter('flow'):
		for child in flow:
			if child.tag == "material":
				for mattext in child.iter('mattext'):
					text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ReplaceParagraphTags(text) #replace paragraph tags with line breaks so string.splitlines() will work correctly
	text = text.splitlines()

	if text[-1].find("image(") == -1:
		lastLine = text[-1]
		lastLine = ProcessText(lastLine, "pg")

		text = text[:-1]
	else:
		lastLine = ""

	firstLines=""
	for line in text:
		if not line == "":
			firstLines+= "<p>" + line + "</p>" #add paragraph tags back so ProcessText() can process text correctly
	firstLines = ProcessText(firstLines)

	return firstLines, lastLine

def GetChoicesMultiSelect(item):
	choicesDict = dict()
	correctID = list()
	incorrectID = list()
	correct = list()
	incorrect = list()

	for flow in item.iter('flow'):
		for response in flow.iter('response_lid'):
			for label in response.iter('response_label'):
				id = label.get('ident')
				for mattext in label.iter('mattext'):
					choiceText = mattext.text
					choiceText = ProcessText(choiceText, "pg")
				choicesDict.update({id:choiceText})

	for resprocessing in item.iter('resprocessing'):
		for respcondition in resprocessing.iter('respcondition'):
			title = respcondition.get('title')

			#there are two ways choices can be marked correct/incorrect in the xml file
			#they are determined by the title in the "respcondition tag"
			if title is not None:
				if title.find("Response")==-1:
					#title="Scoring for correct answers"
					for conditionvar in respcondition.iter('conditionvar'):
						for varequal in conditionvar:
							if varequal.tag == "varequal":
								correctID.append(varequal.text)

						for notTag in conditionvar:
							if notTag.tag == "not":
								for varequal in notTag:
									if varequal.tag == "varequal":
										incorrectID.append(varequal.text)

					break
				else:
					#title="Response condition"
					for respID in respcondition.iter('varequal'):
						id = respID.text
						break
					for setvar in respcondition.iter('setvar'):
						if setvar.get('varname')=="D2L_Correct":
							correctID.append(id)
						else:
							incorrectID.append(id)
			
	for id in correctID:
		correct.append(choicesDict[id])

	for id in incorrectID:
		incorrect.append(choicesDict[id])

	return correct, incorrect

def GetProblemTextOrdering(item):

	text = ""
	
	#go through the tree and find the main problem text. 
	#implementation's a bit messy, but it prevents the algorithm from grabbing the options
	for flow in item.iter('flow'):
		for child in flow:
			if child.tag == "material":
				for mattext in child.iter('mattext'):
					text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ProcessText(text)

	return text

def GetChoicesOrdering(item):
	
	choicesDict = dict()
	orderingID = dict()
	ordering = dict()

	for flow in item.iter('flow'):
		for response in flow.iter('response_grp'):
			for label in response.iter('response_label'):
				id = label.get('ident')
				for mattext in label.iter('mattext'):
					choiceText = mattext.text
					choiceText = ProcessText(choiceText, "pg")
				choicesDict.update({id:choiceText})

	for resprocessing in item.iter('resprocessing'):
		for respcondition in resprocessing.iter('respcondition'):
			title = respcondition.get('title')

			if title is not None:
				for varequal in respcondition.iter('varequal'):
					id = varequal.get('respident')
					order = varequal.text
					orderingID.update({id:order})
					break
	
	for id, text in choicesDict.items():
		ordering.update({text:orderingID[id]})

	return ordering

def GetHints(item):

	text = ""

	for hint in item.iter('hint'):
		for mattext in hint.iter('mattext'):
			text+=mattext.text;

	text = ProcessText(text)
	text = text.replace("\n","")

	return text

def GetProblemTextLongAnswer(item):

	text = ""

	for flow in item.iter('flow'):
		#get problem text
		for mattext in flow.iter('mattext'):
			if mattext.text is not None:
				text+=mattext.text
		for matimage in flow.iter('matimage'):
			imgURL = matimage.get('uri')
			imgTag = "<p><img src=\"" + imgURL + "\"/></p>"
			text+=imgTag

	text = ProcessText(text)

	return text

def WriteToDebugFileArithmetic(item, debugFile):

	text = GetProblemTextArithmetic(item)
	debugFile.write("\t\t" + text + "\n\n\n") 

	text = GetVariablesArithmetic(item)
	debugFile.write("\t\t" + text + "\n\n\n") 

	text, text2, text3 = GetAnswersArithmetic(item)
	debugFile.write("\t\t" + text + "; " + text2 + "-" + text3 + "\n\n\n") 

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def WriteToDebugFileMultiSelect(item, debugFile):

	firstLines, lastLine = GetProblemTextMultiSelect(item)
	debugFile.write("\t\t" + firstLines + "\n\n" + lastLine + "\n\n\n")
						 
	correct, incorrect = GetChoicesMultiSelect(item)

	debugFile.write("\t\tCorrect:\n")
	for c in correct:
		debugFile.write("\t\t"+c+"\n")

	debugFile.write("\t\tIncorrect:\n")
	for i in incorrect:
		debugFile.write("\t\t"+i+"\n")

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def WriteToDebugFileTrueFalse(item, debugFile):

	text = GetProblemTextTrueFalse(item)
	debugFile.write("\t\t" + text + "\n\n\n") 

	text = GetAnswersTrueFalse(item)
	debugFile.write("\t\t" + str(text) + "\n\n\n") 

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def WriteToDebugFileMultipleChoice(item, debugFile):

	text = GetProblemTextMultipleChoice(item)
	debugFile.write("\t\t" + text + "\n\n\n") 

	choices,correctChoice = GetChoicesMultipleChoice(item)
	for choice in choices:
		debugFile.write("\t\t"+choice+"\n")
	debugFile.write("\t\tCorrect: " + correctChoice + "\n\n\n") 

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def WriteToDebugFileLongAnswer(item,debugFile):

	text = GetProblemTextLongAnswer(item)
	debugFile.write("\t\t" + text + "\n\n\n") 

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def WriteToDebugFileOrdering(item,debugFile):
	
	text = GetProblemTextOrdering(item)
	debugFile.write("\t\t" + text + "\n\n\n") 
	ordering = GetChoicesOrdering(item)
	for k,v in ordering.items():
		debugFile.write("\t\t" + str(v) + ". " + k + "\n")

	text = GetHints(item)
	if text != "":
		debugFile.write("\t\tHint:" + text + "\n\n\n") 

def pgStartText():
	text = ""
	text+= "##############################################################\n\n"
	text+= "DOCUMENT();\n\n"
	text+= "loadMacros(\n"
	text+= "\t\"PGstandard.pl\",\t# Standard macros for PG language\n"
	text+= "\t\"MathObjects.pl\",\n"
	text+= "\t\"PGML.pl\",\n"
	text+= "\t\"parserPopUp.pl\",\n"
	text+= "\t\"parserMultiAnswer.pl\",\n"
	text+= "\t\"parserRadioButtons.pl\",\n"
	text+= "\t\"PGchoicemacros.pl\",\n"
	text+= "\t#\"source.pl\",\t# allows code to be displayed on certain sites.\n"
	text+= "\t#\"PGcourse.pl\",\t# Customization file for the course.\n"
	text+= "\t);\n\n"
	text+= "TEXT(beginproblem());\n\n"
	text+= "##############################################################\n"
	text+= "#\n#  Setup\n#\n#\n\n"

	return text

def pgEndText():
	text = ""
	text+= "##############################################################\n\n"
	text+= "ENDDOCUMENT();"

	return text

def WriteProblemToFileBlank(item,itemName,sectionName,folderName, singleFolder = False):


	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())
	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileArithmetic(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#main text
	text = GetVariablesArithmetic(item)
	pgFile.write("#given\n"+ text + "\n\n") 

	text = GetProblemTextArithmetic(item)
	pgFile.write("BEGIN_PGML\n\n" + text + "\n\n[____]\n\n") 

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	#anwer field
	formula, tol, toltype = GetAnswersArithmetic(item)
	answer = ""
	answer+="ANS(num_cmp("+formula+", "
	if toltype == "percent":
		answer+='reltol => ' + tol
	else: 
		answer+='reltol => ' + tol
	answer+=", ));"

	pgFile.write(answer+"\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileOrdering(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#main text
	text = GetProblemTextOrdering(item)
	pgFile.write("BEGIN_PGML\n\n" + text + "\n\n") 

	ordering = GetChoicesOrdering(item)
	order = list(ordering.keys())
	random.shuffle(order)

	for answer in order:
		pgFile.write("[____]{"+ ordering[answer] +"}" + answer + "  \n")

	pgFile.write("\n\n")

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileTrueFalse(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#true or false
	trueOrFalse = GetAnswersTrueFalse(item)

	mc = ""
	mc+="$mc = RadioButtons(\n"
	mc+="\t[\"True\",\"False\"],\n"
	mc+="\t\"" + str(trueOrFalse) + "\"\n"
	mc+=");"

	pgFile.write(mc + "\n\n")

	#main text
	text = GetProblemTextTrueFalse(item)
	pgFile.write("BEGIN_PGML\n\n" + text + "\n\n[@ $mc->buttons() @]*\n\n") 

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	pgFile.write("ANS($mc->cmp());\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileMultipleChoice(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#setting up multiple choice
	choices, correctChoice = GetChoicesMultipleChoice(item)
	correctChoice = RemoveQuotesInChoices(correctChoice)

	mc = ""
	mc+="$mc = RadioButtons(\n"
	mc+="\t["

	for i in range(0,len(choices)):
		choice = RemoveQuotesInChoices(choices[i])
		mc+="\"" + choice + "\""
		if i < len(choices)-1:
			mc+=", "

	mc+="],\n"
	mc+="\t\"" + correctChoice + "\"\n"
	mc+=");"

	pgFile.write(mc + "\n\n")

	#main text
	text = GetProblemTextMultipleChoice(item)
	pgFile.write("BEGIN_PGML\n\n" + text + "  \n[@ $mc->buttons() @]*\n\n") 

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	pgFile.write("ANS($mc->cmp());\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileMultiSelect(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#setting up multi-select
	correct, incorrect = GetChoicesMultiSelect(item)
	firstLines, lastLine = GetProblemTextMultiSelect(item)
	
	lastLine = RemoveQuotesInChoices(lastLine)

	mc = ""
	mc+="$mc = new_checkbox_multiple_choice();\n"
	mc+="$mc->qa(\n"

	mc+="\t\""+lastLine+"\",\n"
	
	for i in range(0,len(correct)):
		choice = RemoveQuotesInChoices(correct[i])
		mc+="\t\""+choice+"\""
		if i < len(correct)-1:
			mc+=", \n"

	mc+="\n);\n"
	mc+="$mc->extra(\n"

	for i in range(0,len(incorrect)):
		choice = RemoveQuotesInChoices(incorrect[i])
		mc+="\t\""+choice+"\""
		if i < len(incorrect)-1:
			mc+=", \n"

	mc+="\n);"

	pgFile.write(mc + "\n\n")

	#main text
	pgFile.write("BEGIN_PGML\n\n")
	pgFile.write(firstLines)
	pgFile.write("\n\n[@ $mc->print_q() @]*\n[@ $mc->print_a() @]*\n\n") 

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	pgFile.write("ANS(checkbox_cmp($mc->correct_ans()));\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def WriteProblemToFileLongAnswer(item,itemName,sectionName,folderName, singleFolder = False):

	#make sure filenames are valid
	itemName = re.sub('\W',"",itemName)
	sectionName = re.sub('\W',"",sectionName)

	if not singleFolder:
		directory = os.path.join(os.getcwd(),folderName,sectionName)
	else:
		directory = os.path.join(os.getcwd(),folderName)

	pgFileName = os.path.join(directory,itemName + ".pg")

	if not os.path.exists(directory): 
		os.makedirs(directory)

	fileCount = 1
	while(os.path.isfile(pgFileName)):
		fileCount+=1;
		pgFileName = os.path.join(directory,itemName + str(fileCount) + ".pg")

	pgFile = codecs.open(pgFileName,"w","utf-8")

	pgFile.write(pgStartText())

	#main text
	text = GetProblemTextLongAnswer(item)
	pgFile.write("BEGIN_PGML\n\n" + text + "\n\n[____]{\"$anything\"}\n\n") 

	text = GetHints(item)
	if text != "":
		pgFile.write("_Hint:" + text + "_\n\n") 

	pgFile.write("END_PGML\n\n")

	pgFile.write(pgEndText())
	pgFile.close()

def RemoveQuotesInChoices(text):
	if not text.find("\"")==-1:
		text = re.sub(r'\"(?=[^\\`]|$[^\)\]]?)', "\'", text)
		text = re.sub(r'\"(?=[\\`][\)\]])', "in", text)
		text = re.sub(r'\'(?=[\\`][\)\]])', "ft", text)
	return text


tree = ET.parse(questionDB)
root = tree.getroot()

#directory for converted files
if not os.path.exists(folderName): 
    os.makedirs(folderName)
else:
	shutil.rmtree(folderName) #remove old directory
	os.makedirs(folderName)
	
#parse .XML and convert files
items = 0;

debugFile = codecs.open("parse.xml","w","utf-8")

for section in root.iter('section'):

		hasItems = False
		#check if section/problem set has questions
		for child in section:
			if (child.tag=='item'):
				hasItems = True
				break;

		#if section is not empty
		if hasItems:
			#use D2L unique identity if section title is empty
			if section.get('title') is not None:
				sectionName = section.get("title")
			else:
				sectionName = section.get("ident")
			
			debugFile.write("SECTION: "+ sectionName + "\n\n\n")
			
			for item in section:
				if (item.tag=='item'):
					items+=1
					#use D2L unique label if question title is empty
					if item.get('title') is not None:
						itemName = item.get("title")
					else:
						itemName = item.get("ident")

					debugFile.write('\n\tPROBLEM #' + str(items) + ": " + itemName)

					#find the question type metadata tag
					for qti_metadatafield in item.iter('qti_metadatafield'):
						#if the fieldlabel doesn't indicate question type, go to the next one
						#if it does, then get the question's type
						for field in qti_metadatafield:
							if (field.tag == "fieldlabel" and field.text != "qmd_questiontype"):
								break

							if (field.tag == "fieldentry"):
								questionType = field.text

					debugFile.write("     [" + questionType + "]\n\n\n") 	

					if (questionType == "Ordering"):
						#pass

						WriteProblemToFileOrdering(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileOrdering(item,debugFile)

					elif (questionType == "Long Answer"):
						#pass

						WriteProblemToFileLongAnswer(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileLongAnswer(item, debugFile)

					elif (questionType == "Multiple Choice"):
						#pass

						WriteProblemToFileMultipleChoice(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileMultipleChoice(item, debugFile)

					elif (questionType == "True/False"):
						#pass

						WriteProblemToFileTrueFalse(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileTrueFalse(item, debugFile)

					elif (questionType == "Multi-Select"):
						#pass

						WriteProblemToFileMultiSelect(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileMultiSelect(item, debugFile)

					else: #significant figures + arithmetic type + anything else
						#pass
							
						WriteProblemToFileArithmetic(item,itemName,sectionName,folderName, singleFolder)

						WriteToDebugFileArithmetic(item, debugFile)
						


			debugFile.write("\n\n\n\n")
		else:
			continue;

debugFile.close()

#copy images over
directory = os.getcwd();
fileDict = dict();
filenameList = list()

for dirpath, dirname, filenames in os.walk(directory):
	for filename in [f for f in filenames if f.endswith(".pg")]:
		filenameList.append(filename);
		fileDict.update({filename: dirpath})

print("{} .pg files found.".format(len(filenameList)));

for file in filenameList:
	filePath = os.path.join(fileDict[file],file)
	f = codecs.open(filePath, "r", "utf-8")
	content = f.read()
	f.close()

	images = re.findall('image\(.*?[\"\'](.*?)[\"\'].*?\)', content)

	if len(images) == 1:
		try:
			ext = re.findall('(?<=\.)([^\.]*?$)', images[0])[0]
			ext = ext.lower() #WebWork can't handle all caps extensions such as .PNG
			if ext == "jpeg": #WebWork doesn't recognize jpeg as jpg
				ext = "jpg"
		except:
			ext = "png" #default format: png
		src = os.path.join(directory,images[0])
		dst = os.path.join(fileDict[file],file.replace(".pg","."+ext))
		content = content.replace(images[0],file.replace(".pg","."+ext))
		copyfile(src,dst)

	else:
		for i in range(0, len(images)):
			try:
				ext = re.findall('(?<=\.)([^\.]*?$)', images[i])[0]
			except:
				ext = "png" #default format: png
			src = os.path.join(directory,images[i])
			dst = os.path.join(fileDict[file],file[:-3]+str(i+1)+"."+ext)

			content = content.replace(images[i],file[:-3]+str(i+1)+"."+ext, 1)
			copyfile(src,dst)

	f = codecs.open(filePath, "w", "utf-8")
	f.write(content)
	f.close()	

input();