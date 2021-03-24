import bpy
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

# https://www.tutorialfor.com/blog-284275.htm
def prettyxml(element, indent="\t", newline="\n", level=0):
    if element:
        if element.text == None or element.text.isspace():
            element.text=newline + indent * (level + 1)
        else:
            element.text=newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    temp=list(element)
    for subelement in temp:
        if temp.index(subelement)<(len(temp)-1):
            subelement.tail=newline + indent * (level + 1)
        else:
            subelement.tail=newline + indent * level
        prettyxml(subelement, indent, newline, level=level + 1)