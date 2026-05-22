import streamlit as st

st.header("使用说明")
st.markdown('''
### Idocx文件相关
文件预处理和知识库处理只能上传一个文件，否则只能选择下载一个处理后的文件。
### IIfbd文件相关
fbd文件路径必须为网络路径，且具有读写权限。
### III与扣子对话         
modules下的“bots.json”文件保存着token下已发布的机器人列表，若要重新获取机器人列表，请删除该文件，并重启程序。
### IV数传音频文件上传
modules下的“token.txt”文件保存着数传访问需要的token，若音频数据建立不成功，就更新tpken，并重启程序。   
''')
