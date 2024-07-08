import os
import re
from .utils import xml2dict, match_BytesExtra, timestamp2str


def extract_text_content(StrContent):
    return {"src": "", "msg": StrContent}


def extract_image_content(DictExtra):
    DictExtra_str = str(DictExtra)
    img_paths = [i for i in re.findall(r"(FileStorage.*?)'", DictExtra_str)]
    img_paths = sorted(img_paths, key=lambda p: "Image" in p, reverse=True)
    if img_paths:
        img_path = img_paths[0].replace("'", "")
        img_path = [i for i in img_path.split("\\") if i]
        img_path = os.path.join(*img_path)
        return {"src": img_path, "msg": "图片"}
    else:
        return {"src": "", "msg": "图片"}


def extract_voice_content(StrContent,
                          StrTalker,
                          CreateTime,
                          IsSender,
                          MsgSvrID):
    tmp_c = xml2dict(StrContent)
    voicelength = tmp_c.get("voicemsg", {}).get("voicelength", "")
    transtext = tmp_c.get("voicetrans", {}).get("transtext", "this is a transcription")
    if voicelength.isdigit():
        voicelength = int(voicelength) / 1000
        voicelength = f"{voicelength:.2f}"
    msg = f"语音时长：\{voicelength}秒\n\
        翻译结果：{transtext}" if transtext else f"语音时长：{voicelength}秒"
    src = os.path.join(
        "audio",
        f"{StrTalker}",
        f"{CreateTime.replace(':', '-').replace(' ', '_')}_{IsSender}_{MsgSvrID}.wav")
    return {"src": src,
            "msg": msg,
            'duration': voicelength,
            'transcription': transtext}


def extract_video_content(DictExtra):
    DictExtra_str = str(DictExtra)
    video_paths = [i for i in re.findall(r"(FileStorage.*?)'", DictExtra_str)]
    video_paths = sorted(video_paths, key=lambda p: "mp4" in p, reverse=True)
    if video_paths:
        video_path = video_paths[0].replace("'", "")
        video_path = [i for i in video_path.split("\\") if i]
        video_path = os.path.join(*video_path)
        return {"src": video_path, "msg": "视频"}
    else:
        return {"src": "", "msg": "视频"}


def extract_emoji_content(StrContent):
    content_tmp = xml2dict(StrContent)
    cdnurl = content_tmp.get("emoji", {}).get("cdnurl", "")
    if cdnurl:
        return {"src": cdnurl, "msg": "表情"}
    else:
        return {"src": "", "msg": "表情"}


def extract_file_content(DictExtra):
    url = match_BytesExtra(DictExtra)
    file_name = os.path.basename(url)
    return {"src": url, "msg": file_name}


def extract_forwarded_message_content(CompressContent):
    content_tmp = xml2dict(CompressContent)
    title = content_tmp.get("appmsg", {}).get("title", "")
    des = content_tmp.get("appmsg", {}).get("des", "")
    recorditem = content_tmp.get("appmsg", {}).get("recorditem", "")
    recorditem = xml2dict(recorditem)
    return {"src": recorditem,
            "msg": f"{title}\n{des}",
            'title': title,
            'des': des}


def extract_quoted_message_content(CompressContent):
    content_tmp = xml2dict(CompressContent)
    appmsg = content_tmp.get("appmsg", {})
    title = appmsg.get("title", "")
    refermsg = appmsg.get("refermsg", {})
    displayname = refermsg.get("displayname", "")
    display_content = refermsg.get("content", "")
    display_createtime = refermsg.get("createtime", "")
    display_createtime = timestamp2str(
        int(display_createtime)) if display_createtime.isdigit() else display_createtime
    # '看来你一般睡的挺晚的啊[Smart]\n\n[引用](2023-07-17 01:19:32)五餅二魚:现在还在屋里面上蹿下跳的'
    msg = f"{title}\n\n[引用]({display_createtime}){displayname}:{display_content}"
    return {"src": "",
            "msg": msg,
            'reply_with': title,
            'reply_to': display_content,
            'reply_to_name': displayname}


def extract_transfer_content(CompressContent):
    content_tmp = xml2dict(CompressContent)
    feedesc = content_tmp.get("appmsg", {}).get(
        "wcpayinfo", {}).get("feedesc", "")
    return {"src": "",
            "msg":
            f"转账：{feedesc}",
            "amount": feedesc}


def extract_card_content(xml_str):
    xml_dict = xml2dict(xml_str)
    return {
        "title": xml_dict['appmsg'].get('title', ''),
        "src": xml_dict['appmsg'].get('url', ''),
        "des": xml_dict['appmsg'].get('des', ''),
        "sourcedisplayname": xml_dict['appmsg'].get('sourcedisplayname', '')
    }


def extract_recommendation_content(self, StrContent):
    xml_dict = xml2dict(StrContent)
    return xml_dict


def extract_other_type_content(DictExtra, type_name):
    url = match_BytesExtra(DictExtra)
    return {"src": url, "msg": type_name}


def extract_call_content(DisplayContent):
    return {"src": "", "msg": f"语音/视频通话[{DisplayContent}]"}


def get_talker(IsSender, StrTalker, bytes_extra, BytesExtra):
    if IsSender == 1:
        return "我"
    else:
        if StrTalker.endswith("@chatroom"):
            if bytes_extra:
                try:
                    talker = bytes_extra['3'][0]['2'].decode(
                        'utf-8', errors='ignore')
                    if "publisher-id" in talker:
                        return "系统"
                    return talker
                except (KeyError, AttributeError):
                    decoded_string = BytesExtra.decode(
                        'ascii', errors='ignore')
                    match = re.search(r'\x12\t([a-zA-Z0-9]+)', decoded_string)
                    return match.group(1) if match else "微信系统"

        else:
            return StrTalker
