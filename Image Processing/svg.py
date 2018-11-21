#Description:
#Adds the Creative Commons Lisence to all .svg files in a directory exported by Adobe Illustrator, etc.
#Must have the .svg License file in the same directory as this script and the target .svg's.

#How to use:
#Drop this .py file, and Creative Commons License file (in .svg format) in a directory where .svg files still lack the Lisence
#Run this script.
#Collect the updated .svg files in a newly created folder.
#Export location, Lisence file name, and Lisence scale can be changed by changing the variables below.
#This script is typically used before .svg files are batch converted to .png files.

import os
import xml.etree.ElementTree as ET
from svgutils.compose import *
import shutil

folderName = "Converted SVGs";
ccFileName = "cc-engineering.svg";
scale = 1.3;

#directory for converted files
if not os.path.exists(folderName): 
    os.makedirs(folderName)
else:
	shutil.rmtree(folderName) #remove old directory
	os.makedirs(folderName)

cwd = os.getcwd(); #current working directory
directory = os.listdir(os.getcwd());
fileList = list();

#scan for all svg files under directory
for filename in directory:
    if (filename.endswith(".svg")&(filename!=ccFileName)):
        fileList.append(filename);

print("{} .svg files found.".format(len(fileList)));

#get data from the creative commons svg
tree = ET.parse(ccFileName);
root = tree.getroot();

try:
	ccHeight = float(root.attrib['height']);
	ccWidth = float(root.attrib['width']);
except:
	viewBoxData = root.attrib['viewBox'];
	data = viewBoxData.split();
	ccHeight = float(data[3]);
	ccWidth = float(data[2]);

#set temporary file name
tempSVG = "temp.svg";

#cycle through all svg files
for target in fileList:
	tree = ET.parse(target);
	root = tree.getroot();

	#data processing
	try:
		viewBoxData = root.attrib['viewBox'];
		data = viewBoxData.split();

		xOffset = -1*float(data[0]);
		yOffset = -1*float(data[1]);

		height = float(data[3]);
		width = float(data[2]);
	except:
		height = float(root.attrib['height']);
		width = float(root.attrib['width']);
		xOffset = 0;
		yOffset = 0;

	ccLocX = width - ccWidth*scale;
	ccLocY = height;

	newFilename = cwd+"\\"+folderName+"\\"+target;

	#join svgs with svgutils
	Figure(str(width),str(height + scale*ccHeight),
		   Panel(
			   SVG(target).move(xOffset,yOffset)),
		   Panel(
			   SVG(ccFileName).scale(scale)).move(ccLocX,ccLocY)
		   ).save(tempSVG);

	#remove ugly circle junctions, fix font family spelling
	tree = ET.parse(tempSVG);
	root = tree.getroot();

	for tag in root.iter():
		for group in tag.findall("{http://www.w3.org/2000/svg}g"):
			if 'c_partid' in group.attrib:
				if group.attrib['c_partid'] == 'part_junction':
					tag.remove(group)
		for group in tag.findall("{http://www.w3.org/2000/svg}text"):
			if 'style' in group.attrib:
				text = group.attrib['style'];
				text = text.replace("SegoeScript", "Segoe Script" )
				group.set('style',text)

	tree.write(newFilename)

if os.path.isfile(tempSVG):
	os.remove(tempSVG);

print("SVG's converted.")
input();