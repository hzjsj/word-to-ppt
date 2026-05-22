#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from lxml import etree
from unicode_map import unicode_map
import xml.etree.ElementTree as ET
import re

# MathML to LaTeX conversion with XSLT from Vasil Yaroshevich
base_path = os.path.dirname(os.path.realpath(__file__))
xslt_file = os.path.join(base_path, 'mmltex', 'mmltex.xsl')
xslt = etree.parse(xslt_file)
transform = etree.XSLT(xslt)

omathxslt = etree.parse(os.path.join(base_path, 'ommltex', 'OMML2MML.XSL'))
omathtransform = etree.XSLT(omathxslt )
pattern = r'\\u([0-9a-fA-F]{4})'

def replace_unicode(match):
    # 获取匹配到的 Unicode 转义序列
    unicode_str = match.group(1)
    # 将 Unicode 转义序列转换为对应的字符
    char = chr(int(unicode_str, 16))
    return char

def mathml2latex(mathml_block:str):
    # Preprocess to remove aliases
    mathml_block = mathml_block.replace('<<', '&lt;<').replace('>>', '>&gt;')
    dom = etree.fromstring(mathml_block)
    return transform(dom)
def unicode2latex(latex_block):
    latex_text = str(latex_block, 'utf-8').encode('ascii', 'backslashreplace')
    for utf_code, latex_code in unicode_map.items():
        latex_text = str(latex_text).replace(utf_code, latex_code)
    latex_text = latex_text.replace('\\\\', '\\')                          # "\\" --> "\"
    latex_text = re.sub(r'\\textcolor\[rgb\]\{[0-9.,]+\}', '', latex_text) # "\textcolor[rgb]{...}" --> ""
    latex_text = latex_text.replace('\\ ~\\ ', '{\\sim}')                  # " ~ " --> "{\sim}"
    latex_text = latex_text[len('b\''):][:-len('\'')]                      # b'...' --> ...
    latex_text = re.sub(r'^\$ ', '$', latex_text)                          # "$ " --> "$"
    latex_text = latex_text.replace('{\\ }', '\\ ')                        # "{ }" --> " "
    latex_text = re.sub(r' \}', '}', latex_text)                           # " }" --> "}"
    latex_text = latex_text.replace('\\n\\[\\n\\t', '$$').replace('\\n\\]', '$$')
    return latex_text

def omath_convert(omathele:etree._Element):
    mathml_block=  etree.tostring(omathtransform(omathele),pretty_print=False).decode('utf-8').replace('<m','<mml:m').replace('</m','</mml:m')
    latex_block = mathml2latex(mathml_block)
    latex_text = str(latex_block, 'utf-8')
    return latex_text

def omathstr_convert(omathstr:str):
    omathele=etree.fromstring(omathstr.replace('<m:oMath>','<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'))
    mathml_block=  etree.tostring(omathtransform(omathele),pretty_print=False).decode('utf-8').replace('<m','<mml:m').replace('</m','</mml:m')
    latex_block = mathml2latex(mathml_block)
    latex_text = str(latex_block, 'utf-8')
    return latex_text


def mml_convert(mml_block):
    # 解析 XML 
    root = ET.fromstring(mml_block)
    # 添加命名空间
    root.tag = 'mml:math'
    root.set('xmlns:mml', 'http://www.w3.org/1998/Math/MathML')
    # 遍历子元素并添加命名空间前缀
    for elem in root.iter():
        if elem.tag != root.tag:
            elem.tag = 'mml:' + elem.tag
    # 生成新的 XML 字符串
    new_mathml_str = ET.tostring(root, encoding='unicode')
    latex_block = mathml2latex(new_mathml_str)
    latex_text = unicode2latex(latex_block)
    return re.sub(pattern, replace_unicode, latex_text)


if __name__ == "__main__":
    # from docx import Document
    # from docx.oxml.ns import qn as wdqn
    # doc=Document(r"C:\Users\Administrator\Desktop\cos.docx")
    # input_file = open(sys.argv[1], "r", encoding="utf-8")
    # output_file = open(sys.argv[2], "w", encoding="utf-8")
    pass
    