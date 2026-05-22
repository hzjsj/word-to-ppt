import streamlit as st
from docx import Document
import re
from modules.数传音频接口 import *
from io import BytesIO
uuid_list = []

def add_text(innerHTML, speaker_name):
    global textList
    speaker = speakers[speaker_name].copy()
    speaker["innerHTML"] = innerHTML
    uuid = generate_random_string()
    while uuid in uuid_list:
        uuid = generate_random_string()
    uuid_list.append(uuid)
    speaker["uuid"] = uuid
    textList.append(speaker)

def add_repeat_text():
    global repeat_text, Q_type
    for index, repeat in enumerate(repeat_text):  # 第一遍
        if index == len(repeat_text) - 1:
            if repeat[1] == ":":
                add_text(repeat[2:] + tingdun % times[Q_type][1], repeat[:2])
            else:
                add_text(repeat + tingdun % times[Q_type][1], "M:")
        else:
            if repeat[1] == ":":
                add_text(repeat[2:] + tingdun % "1", repeat[:2])
            else:
                add_text(repeat + tingdun % "1", "M:")
    for index, repeat in enumerate(repeat_text):  # 第二遍
        if repeat[1] == ":":
            if index == len(repeat_text) - 1:
                add_text(repeat[2:] + tingdun % times[Q_type][2], repeat[:2])
            else:
                add_text(repeat[2:] + tingdun % "1", repeat[:2])
        else:
            if index == len(repeat_text) - 1:
                add_text(repeat + tingdun % times[Q_type][2], "W:")
            else:
                add_text(repeat + tingdun % "1", "W:")
    repeat_text = []

#1.生成文本框，指定上传文件夹id
folderId=st.text_input("请输入上传文件夹id")
# 2. 生成文件上传按钮，供用户选择或拖拽docx类型文件并上传
uploaded_file = st.file_uploader("上传听力音频docx文件", type="docx",)
co1,co2=st.columns(2)
button1 = co1.button("上传至数传")
# button2 = co2.button("合成音频")
app = App()
st.toast(app.connect())


if uploaded_file :
    if button1:
        
        

        if not folderId:
            folderId = app.add_folder(uploaded_file.name[:-5])

        doc = Document(BytesIO(uploaded_file.read()))
        title = ""
        for para in doc.paragraphs:
            style = para.style.name
            text = para.text
            if style == "Heading 1":  # 一级标题
                if title:
                    add_repeat_text()
                    info=app.create_audio(title, folderId, textList, "")

                    st.toast(title+str(info))
                title = text
                textList, last_para_text = [], ""
                repeat_text, Q_type = [], "Ⅰ"
                innerHTML = (
                    qianzou
                    + tingdun % "3"
                    + text.replace("　", tingdun % "0.5")
                    + tingdun % "1"
                )
                (
                    add_text(innerHTML, "中文")
                    if re.search(r"[\u4e00-\u9fff]+", text)
                    else add_text(innerHTML, "英文")
                )
            elif style == "Heading 2":  # 二级标题
                title += text
                innerHTML = text.replace("　", tingdun % "0.5") + tingdun % "1"
                (
                    add_text(innerHTML, "中文")
                    if re.search(r"[\u4e00-\u9fff]+", text)
                    else add_text(innerHTML, "英文")
                )
            else:
                if re.match(r"^[ⅠⅡⅢⅣ]", text):  # 题型
                    add_repeat_text()
                    Q_type = re.match(r"^[ⅠⅡⅢⅣ]", text).group()
                    add_text(text + tingdun % "0.5", "中文")
                elif re.match(r"^[ⅠⅡⅢⅣ]+", last_para_text):  # 题型的下一段
                    text = text.replace("每空", "每" + duoyin)
                    add_text(text + tingdun % times[Q_type][0], "中文")
                elif re.match(r"^\d|听下面", text):  # 小题说明
                    add_repeat_text()
                    if re.match(r"^\d|听下面", text).group() == "听下面":
                        add_text(text + tingdun % "10", "中文")
                    else:
                        add_text(text + tingdun % "0.5", "英文")
                elif re.match(r"^M:|^W:", text):  # 以M: 或W: 开头
                    repeat_text.append(text)
                else:
                    repeat_text.append(text)
            last_para_text = text
        add_repeat_text()
        info=app.create_audio(title, folderId, textList, "")
        st.toast(title+str(info))