import streamlit as st
from modules.oprate_img import *

# 注入自定义 CSS
st.markdown("""<style>div[data-testid="stMarkdownContainer"]{font-size: 18px;}
div[data-testid="stColumn"] {background-color: #efe6e6;padding: 10px 20px;border-radius: 20px;}</style>""", unsafe_allow_html=True)


uploaded_file = st.text_input("请输入fbd文件路径(必须使用网络路径)：")
selected_options,columns=[],st.columns(2)
for col,a,b in zip(columns,*zip(*{'fbd文件导入处理':['1.通用学科','2.数学学科','3.化学学科（转反应式）'],'fbd问题处理（只能选择一项）':["0.备份文件恢复",'1.图片路径自动补全','2.答案图生成'],}.items())):
    with col:
        st.write(a)
        for c in b:
            option=st.checkbox(c)
            if option:
                selected_options.append(c)
button1=columns[0].button("fbd文件导入处理")
if '2.答案图生成' in selected_options:
    selected_option_button = columns[1].selectbox("请选择答案颜色", ["青色", "洋红",])
button2=columns[1].button("fbd问题处理")

if uploaded_file is not None:
    print(selected_options)
    if button1  and selected_options:  #fbd文件导入处理
        fbd=FBD_O(uploaded_file)
        if "1.通用学科" in selected_options:
            fbd.process_fbd()
        if "2.数学学科" in selected_options:
            fbd.process_fbd(reference="modules/fbd2word_数学.fbd")
        if "3.化学学科" in selected_options:
            fbd.process_fbd(reference="modules/fbd2word_化学.fbd")
        fbd.save()
        st.toast("fbd文件导入处理完成！")

    elif button2 and selected_options: #fbd问题处理
        fbd=FBD_Q(uploaded_file)
        if '1.图片路径自动补全' in selected_options:
            fbd.oprate()
        elif '2.答案图生成' in selected_options:
            fbd.oprate(choice=selected_option_button)
        elif '0.备份文件恢复' in selected_options:
            fbd.recover()
        st.toast(f"fbd问题处理完成！")