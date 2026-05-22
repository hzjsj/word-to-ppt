import streamlit as st
from io import BytesIO
import os
from modules.oprate_word import *
from modules.从pdf制作 import docx2pptx
# 注入自定义 CSS
st.markdown("""<style>div[data-testid="stMarkdownContainer"]{font-size: 18px;}
div[data-testid="stColumn"] {background-color: #efe6e6;padding: 10px 20px;border-radius: 20px;}</style>""", unsafe_allow_html=True)

#3.1 docx文件预处理函数
def process_docx1(selected_options,uploaded_file):
    file_content = uploaded_file.read()
    selected_options.sort()
    doc=format_doc(BytesIO(file_content))
    if '1.设置标题' in selected_options:
        doc.set_titlestyle()
    if '2.更改字体' in selected_options:
        doc.set_font(anscolor=selected_option_button)
    if '3.放大图片' in selected_options:
        doc.set_images()
    if '4.更改页面' in selected_options:
        doc.set_page()
    if '5.分页设置' in selected_options:
        doc.set_page_break()
    if '6.标记段落' in selected_options:
        doc.mark_paragraph()
    content =doc.save()
    return content

#3.2 docx文件转成pptx文件
def docx_pptx(selected_options,uploaded_file,):
    file_content = uploaded_file.read()
    bookname=uploaded_file.name[:-5]
    pptfolder=os.path.join("D:/文档/课件制作",bookname)
    docfile=os.path.join(pptfolder,uploaded_file.name)
    if not os.path.exists(pptfolder):
        os.makedirs(pptfolder)
    selected_options.sort()
    doc=format_doc(BytesIO(file_content))
    if '6.标记段落' in selected_options:
        doc.mark_paragraph()
    open(docfile,'wb').write(doc.save())
    if '运行程序' in selected_options:
        docx2pptx(docfile,bookname,pptfolder)
    return f'\\zhangcheng\\课件制作\\{bookname}'
#3.3 知识库处理
def process_docx2(selected_options,uploaded_file):
    file_content = uploaded_file.read()
    selected_options.sort()
    doc=format_doc(BytesIO(file_content))
    if '1.标记标题'  in selected_options:
        doc.mark_title()
    if '2.omath转latex文本' in selected_options:
        doc.omml2latex()
    content =doc.save()
    return content

# 1. 生成文件上传按钮，供用户选择或拖拽docx类型文件并上传
uploaded_files = st.file_uploader("上传docx文件(只能上传一个)", type=["docx","pdf"],accept_multiple_files=True)
# 2. 生成几个复选框，根据用户的不同选择处理文件
selected_options,columns=[],st.columns(3)
for col,a,b in zip(columns,*zip(*{'文件预处理':['1.设置标题','2.更改字体','3.放大图片','4.更改页面','5.分页设置','6.标记段落',],
'制作ppt课件':['运行程序'],
'知识库处理':['1.标记标题','2.omath转latex文本'],}.items())):
    with col:
        st.write(a)
        for c in b:
            option=st.checkbox(c)
            if option:
                selected_options.append(c)

selected_option_button = columns[0].selectbox("请选择答案颜色", ["青色", "洋红",])
button1=columns[0].button("运行文件预处理")
button2=columns[1].button("制作ppt课件")
button3=columns[2].button("知识库处理")

if uploaded_files :
    print(selected_options)
    id=1
    if selected_options:
        for uploaded_file in uploaded_files: #先保存pdf
            if uploaded_file.name.endswith('.pdf'):        
                pptfolder=os.path.join("D:/文档/课件制作",uploaded_file.name[:-4])
                if not os.path.exists(pptfolder):
                    os.makedirs(pptfolder)
                pdffile=os.path.join(pptfolder,uploaded_file.name)
                open(pdffile,'wb').write(uploaded_file.read())

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.docx'):
                if button1 :  #docx文件预处理
                    id+=1
                    st.download_button(label=f"下载处理后的{uploaded_file.name}",
                    data= process_docx1(selected_options,uploaded_file),
                    file_name=uploaded_file.name,
                    mime='application/octet-stream' ,key=f'{id}')
                    st.toast(f"{uploaded_file.name}文件处理成功")

                elif button2 : #制作ppt课件
                    a=docx_pptx(selected_options,uploaded_file)
                    st.toast(f"pptx文件制作成功,保存路径为：{a}")      
                elif  button3:  #docx文件知识库处理
                    id+=1
                    st.download_button(label=f"下载处理后的{uploaded_file.name}",
                    data= process_docx2(selected_options,uploaded_file),
                    file_name=uploaded_file.name,
                    mime='application/octet-stream' ,key=f'{id}')
                    st.toast(f"{uploaded_file.name}文件处理成功")
    else:
        st.error("请选择至少一个处理选项")