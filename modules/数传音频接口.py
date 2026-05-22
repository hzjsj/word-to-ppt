import requests
import json
import random
import string


def generate_random_string(length=7):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


token = open("modules/token.txt", "r", encoding="utf-8").read()

class App:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "accept-language": "zh-CN,zh;q=0.9",
            "access-control-allow-origin": "*",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "token": token,
            "cookie": f"rays7.0Audio_token={token}",
            "Referer": "https://audiobook.5rs.me/rays7/ai/productlist",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

    def connect(self):
        response=self.session.get("https://audiobook.5rs.me/usercenter/v1.0/adviser/getInfo").json()
        return response["message"]




    def list_folder(self, page):  # 列举文件夹
        response = self.session.get(
            f"https://audiobook.5rs.me/audiobook/v1.0/aiAudio/listPageAiAudioRecord?pageNum={page}&pageSize=10&currentPage=1&numPerPage=10"
        ).json()
        return [
            {"title": a["title"], "id": a["id"]} for a in response["data"]["recordList"]
        ]

    def add_folder(self, folderName):  # 创建文件夹
        response = self.session.post(
            "https://audiobook.5rs.me/audiobook/v1.0/folder/addFolder",
            data=json.dumps({"folderName": folderName, "parentId": 0}),
        ).json()
        return response["data"]

    def del_folder(self, folderId):  # 删除文件夹
        response = self.session.post(
            "https://audiobook.5rs.me/audiobook/v1.0/folder/deleteFolders",
            data='{"folderIds":[%s]}' % folderId,
        ).json()
        return response["message"]

    def list_audio(self, folderId):  # 列举音频
        response = self.session.get(
            f"https://audiobook.5rs.me/audiobook/v1.0/aiAudio/listPageAiAudioRecordByFolderId?currentPage=0&numPerPage=10&order=&folderId={folderId}"
        ).json()
        return [
            {"title": a["title"], "id": a["id"]} for a in response["data"]["recordList"]
        ]

    def create_audio(self, title, folderId, textList, id):  # 创建音频
        data = {
            "text": "",
            "format": "audio-16khz-32kbitrate-mono-mp3",
            "title": title,
            "extData": json.dumps(
                {
                    "textTitle": title,
                    "globalBgm": {},
                    "globalPause": {},
                    "editorState": {
                        "chooseAll": False,
                        "textList": textList,
                        "activedId": "magzan",
                        "chosenIds": [],
                    },
                }
            ),
            "letters": 0,
            "textOnly": True,
            "coinCount": 0,
            "templateCode": None,
            "folderId": folderId,
        }
        if id:
            data["id"] = id
        response = self.session.post(
            "https://audiobook.5rs.me/audiobook/v1.0/aiAudio/createAiAudio",
            data=json.dumps(data),
        ).json()
        return response["message"], response["data"]

    def del_audio(self, audioid):  # 删除音频
        response = self.session.post(
            "https://audiobook.5rs.me/audiobook/v1.0/aiAudio/deleteRecordByIds",
            data="[%s]" % audioid,
        ).json()
        return response["message"]

    def get_audio(self, audioid):  # 获取音频
        response = self.session.get(
            f"https://audiobook.5rs.me/audiobook/v1.0/aiAudio/getAiAudioRecordById?id={audioid}"
        ).json()
        return response["data"]

    def generate_audio(self, audio_data, audio_id, folerId):#不成
        response=self.session.post(
            "https://audiobook.5rs.me/audiobook/v1.0/aiAudio/createAiAudio",
            data=json.dumps(
                {
                    "speakerType": 1,
                    "text": audio_data["content"],
                    "format": "audio-16khz-32kbitrate-mono-mp3",
                    "title": audio_data["title"],
                    "extData": audio_data["extData"],
                    "letters": audio_data["letters"],
                    "templateCode": None,
                    "textOnly": False,
                    "coinCount": 1,
                    "folderId": folerId,
                    "id": audio_id,
                }
            ),
        ).json()
        return response


speakers = {
    "中文": {
        "voicer": {
            "id": 5,
            "voicerName": "zh-CN-YunyangNeural",
            "voicerShowName": "扬哥",
            "languageId": 1,
            "langName": None,
            "voicerSex": 1,
            "voicerStyle": "专业、流利的声音，具有多种场景风格。",
            "hiText": "很高兴认识你，有什么能够帮到您?",
            "hiAudioUrl": "https://oss.raysgo.com/oss/spider/audio/mp3/42691d1d041848b48515fe522feb0140.mp3",
            "voicerHeadUrl": "https://oss.5rs.me/oss/uploadfe/png/2d387131e7686f66da8eb9d82e3efcd0.png",
            "role": None,
            "style": None,
            "ageGroup": None,
            "seqNum": 100,
            "roleList": [],
            "styleList": [],
            "rate": "medium",
            "volume": "medium",
            "pitch": "medium",
            "recommendRole": None,
            "recommendStyle": None,
            "recommend": None,
            "speakerType": None,
            "speakerStyle": None,
            "roleStyle": None,
            "defaultSpeed": None,
            "defaultVolume": None,
            "defaultPitch": None,
            "disable": 0,
        },
        "innerHTML": "",
        "uuid": "",
    },
    "英文": {
        "voicer": {
            "id": 41,
            "voicerName": "en-US-RogerNeural",
            "voicerShowName": "Roger",
            "voicerHeadUrl": "https://oss.5rs.me/oss/uploadfe/png/7b78efa39fe3fd03842be719270d2650.png",
            "hiAudioUrl": "https://oss.raysgo.com/oss/spider/audio/mp3/4917d2b3e7174da4a2815e5572b65925.mp3",
            "categoryInfo": ["英语听力", "外语图书"],
            "languageId": 2,
            "language": "英语（美国）",
            "voicerStyle": None,
            "voicerSex": 1,
            "roleList": [],
            "styleList": [],
            "speakerType": 1,
            "rate": "medium",
            "volume": "medium",
            "pitch": "medium",
        },
        "innerHTML": "",
        "uuid": "",
    },
    "M:": {
        "voicer": {
            "id": 24,
            "voicerName": "en-US-GuyNeural",
            "voicerShowName": "Guy",
            "languageId": 2,
            "langName": None,
            "voicerSex": 1,
            "voicerStyle": None,
            "hiText": "Where there is life, there is hope",
            "hiAudioUrl": "https://oss.raysgo.com/oss/spider/audio/mp3/65faa50ffae14454831d188ce2281274.mp3",
            "voicerHeadUrl": "https://oss.5rs.me/oss/uploadfe/png/bd75d6a681b8689bf70c5641f4e60762.png",
            "role": None,
            "style": None,
            "ageGroup": None,
            "isTop": None,
            "seqNum": 100,
            "roleList": [],
            "styleList": [],
            "rate": "medium",
            "volume": "medium",
            "pitch": "medium",
            "recommendRole": None,
            "recommendStyle": None,
            "recommend": None,
            "speakerType": None,
            "speakerStyle": None,
            "roleStyle": None,
            "defaultSpeed": None,
            "defaultVolume": None,
            "defaultPitch": None,
            "disable": 1,
        },
        "innerHTML": "",
        "uuid": "",
    },
    "W:": {
        "voicer": {
            "id": 25,
            "voicerName": "en-US-AriaNeural",
            "voicerShowName": "Aria",
            "voicerHeadUrl": "https://oss.5rs.me/oss/uploadfe/png/6bf54419abff8c4d427cf089dd9a0f34.png",
            "hiAudioUrl": "https://oss.raysgo.com/oss/spider/audio/mp3/1ed008982a3d4c0b88531b49dae94b26.mp3",
            "categoryInfo": ["英语听力", "外语图书"],
            "languageId": 2,
            "language": "英语（美国）",
            "voicerStyle": None,
            "voicerSex": 2,
            "roleList": [],
            "styleList": [],
            "speakerType": 1,
            "rate": "0.9",
            "volume": "medium",
            "pitch": "medium",
        },
        "innerHTML": "",
        "uuid": "",
    },
}


qianzou = '&nbsp;<span class="s-prompt-oS070vV" contenteditable="false" data-label="前奏" data-src="https: //file.5rs.me/oss/transcode/audio/mp3/ec65f9206f10ad53011af86b5c731fb9_audio.mp3">&nbsp;</span>'

tingdun = '<span class="s-pause-oS070vV" contenteditable="false" data-label="%s">&nbsp;</span>'

duoyin = '<span class="s-pinyin-oS070vV" contenteditable="false" data-showlabel="kòng" data-label="kong 4">空</span>'


times = {
    "Ⅰ": ["5", "2", "10"],
    "Ⅱ": ["4", "2", "10"],
    "Ⅲ": ["25", "4", "20"],
    "Ⅳ": ["15", "4", "10"],
}  # 分别是题型说明停顿时间，每小题重复时间，小题结束时间


if __name__ == "__main__":
    app = App()
    print( app.connect())



        # print(app.generate_audio(audio_data,a["id"],"2367"))
