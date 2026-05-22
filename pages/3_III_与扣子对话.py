import streamlit as st
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL
from pypandoc import convert_text
import json,os,requests

st.markdown("""<style>.stDownloadButton > button {border: none;} </style>""", unsafe_allow_html=True)

# 初始化Coze API客户端
coze_api_token = "pat_Tgcf509rRhEr2dgYNnKnAiS734AxdDDs01oRRZgTMJyP5OCtK6IRD3xvOsY9txhF"
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)
@st.cache_data
def get_bots():
    bots=[]
    for workspace in coze.workspaces.list().items:
        try:
            for bot in coze.bots.list(space_id=workspace.id).items:
                bots.append({"bot_id":bot.bot_id,"bot_name":bot.bot_name})
        except:
            pass
    open("modules/bots.json",'w',encoding='utf-8').write(json.dumps(bots,ensure_ascii=False,indent=4))
    return bots

if "bot_id" not in st.session_state:
    if os.path.exists("modules/bots.json"):
        bots=json.loads(open("modules/bots.json",'r',encoding='utf-8').read())
    else:
        bots=get_bots()
    if bots:
        bot_choice=st.selectbox("请选择智能体：", [a["bot_name"] for a in bots])
        if  st.button("确定"):
            st.session_state["bot_id"] = [a["bot_id"] for a in bots if a["bot_name"]==bot_choice][0]
            st.switch_page("pages/3_III_与扣子对话.py")
else:
    # 检查并初始化会话状态
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = ''
        st.session_state["uploaded_file"] = ''
        st.session_state["file_url"]=''
    def md2docx(id,content):
        convert_text(content.replace("\n- *","\n\n- *"), 'docx', format='md',outputfile='out.docx',extra_args=['--atx-headers','--reference-doc=tem.docx'])
        return open('out.docx', 'rb').read()

    st.chat_message("ai").markdown("你好，我是一个智能助手，你可以向我提问任何问题。")
    # 遍历并显示聊天记录中的每一条消息
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            content=message["content"]
            st.markdown(content)
            if message["role"] == "assistant":
                id=message["id"]
                col1, col2 ,col3= st.columns([0.08,0.08,1])
                col1.download_button(label="💾",key=id,data=content,file_name=f"{id}.md",mime="text/plain",)
                col2.download_button(label="📥",key="_"+id,data=md2docx(id,content),file_name=f"{"_"+id}.docx",mime='application/octet-stream',)

    # 处理用户输入的消息和文件
    prompt = st.chat_input("发送消息")
    if prompt:
        st.chat_message("user").markdown(prompt)
        # 调用Coze API进行聊天并实时更新回复消息

        chat = coze.chat.stream(bot_id=st.session_state["bot_id"], user_id='用户', conversation_id=st.session_state["conversation_id"],additional_messages=[Message.build_user_question_text(st.session_state["file_url"]+prompt)])
        st.session_state["messages"].append({"content": st.session_state["file_url"]+prompt, "role": "user"})
        content = ''
        container = st.empty()
        for event in chat:
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                content += event.message.content
                content = content.replace("\\(", "$").replace("\\)", "$")
                message_ai=container.chat_message("assistant")
                message_ai.markdown(content)

            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                id=event.chat.id
                st.session_state["conversation_id"] = event.chat.conversation_id
                st.session_state["messages"].append({"content": content, "role": "assistant","id": id})
                with message_ai:
                    col1, col2 ,col3= st.columns([0.08,0.08,1])
                    col1.download_button(label="💾",key=id,data=content,file_name=f"{id}.md",mime="text/plain",)
                    col2.download_button(label="📥",key="_"+id,data=md2docx(id,content),file_name=f"{"_"+id}.docx",mime='application/octet-stream',)

    uploaded_file=st.file_uploader("上传文件：", type=[])
    
    if uploaded_file is not None :
        if uploaded_file.name!= st.session_state["uploaded_file"]:
            response = requests.post("http://robot.hw0551.com/savefile", headers={ "api-key": "huiwen123456","filetype": ".docx"}, files={"file": uploaded_file.read()})
            st.session_state["uploaded_file"]=uploaded_file.name
            st.session_state["file_url"]=response.json()['message']+" "
        else:
            st.session_state["file_url"]=''
    else:
        st.session_state["uploaded_file"]=''
        st.session_state["file_url"]=''
    print(st.session_state["file_url"])