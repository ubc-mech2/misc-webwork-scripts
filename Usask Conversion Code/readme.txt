#Notes for Using the Usask Conversion Code

MarkdowntoWW.py- Used to convert questions in Markdown format to WebWork format. The question types that can currently be converted are Numerical,
Multiple Choice, True or False, Multiple Answer.
Inputs: Markdown files/Markdown file location 
Outputs:A ".pg"(Webwork format) file for each ".md"(Markdown format) file, a ".def" file for problem sets containing the converted problems,".png" files containing question images,"imagemovingerrors.txt" cointaining
all image moving errors.
**Use Imgtester.py and header.py after running this script**
**You will probably need to install some things if this is your first time. You can use the following commands in a command line:
    pip install --no-index -f https://dist.plone.org/thirdparty/ -U PIL
    py -m pip install pillow
If you have an older version, you may need to uninstall and reinstall using the following commands:
    pip uninstall PIL
    pip uninstall Pillow

Imgtester.py- Use this right after using MarkdowntoWW.py, code renames the images to match the image names in the problem set.
Input:Image file location
Output: Renamed images

Imagescaler.py- Used to resize images while keeping the same ratio.
Inputs:Image height limit, ".pg"(question files) location, image location
Output: Updated question('.pg') files with resized images.

header.py-Used to add or replace headers to the Questions. 
Input: ".pg"(question files) location, ".md" (markdown file) location, header file location
Output: question files with updated headers

