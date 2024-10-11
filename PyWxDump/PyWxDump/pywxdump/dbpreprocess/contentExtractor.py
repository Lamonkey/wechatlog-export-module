import os
import re
from .utils import xml2dict, match_BytesExtra, timestamp2str
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def clean_username(atuserlist):
    if not isinstance("".join(atuserlist), str):
        return atuserlist
    # Use regular expression to find the content within <![CDATA[ ... ]]>
    match = re.search(r'<!\[CDATA\[(.*?)\]\]>', "".join(atuserlist))
    if match:
        # Extract the content and remove any leading commas
        cleaned_usernames = match.group(1).split(',')
        return [username for username in cleaned_usernames if username]
    else:
        return atuserlist


def extract_mentioned_user(bytes_extra):
    '''
    if the inputed userlist contain <atuserlist> tag, extract the userlist
    '''
    # Use regular expression to find the content within <atuserlist> tags
    match = re.search(r'<atuserlist>(.*?)</atuserlist>',
                      str(bytes_extra))
    if match:
        # Split the content by commas to get a list of users
        atuserlist = match.group(1).split(' ')
        cleaned_atuserlist = clean_username(atuserlist)
        return cleaned_atuserlist
    else:
        return []


def extract_text_content(StrContent):
    return {"src": "", "msg": StrContent}


def extract_image_content(DictExtra):
    DictExtra_str = str(DictExtra)
    img_paths = [i for i in re.findall(r"(FileStorage.*?)'", DictExtra_str)]
    img_paths = sorted(img_paths, key=lambda p: "Image" in p, reverse=True)
    compress_img_path, thumbnail_path = None, None
    for path in img_paths:
        img_path = path.replace("'", "")
        img_path = [i for i in img_path.split("\\") if i]
        img_path = os.path.join(*img_path)
        if 'Thumb' in img_path:
            thumbnail_path = img_path
        else:
            compress_img_path = img_path

    return {"src": compress_img_path, "msg": "图片",
            'compressed': compress_img_path,
            'thumbnail': thumbnail_path}


def extract_voice_content(StrContent,
                          StrTalker,
                          CreateTime,
                          IsSender,
                          MsgSvrID):
    tmp_c = xml2dict(StrContent)
    voicelength = tmp_c.get("voicemsg", {}).get("voicelength", "")
    transtext = tmp_c.get("voicetrans", {}).get(
        "transtext", "this is a transcription")
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
    # print(f'\ncontentExtractor, content_tmp: {content_tmp}')
    appmsg = content_tmp.get("appmsg", {})
    title = appmsg.get("title", "")
    refermsg = appmsg.get("refermsg", {})
    refer_id = int(refermsg.get('svrid', -1))
    displayname = refermsg.get("displayname", "") #before it was displayname. chatusr

    # print(f'type for displayname is {type(displayname)}')
    # print(f'contentExtractor displayname: {displayname}')
    chatusr = refermsg.get('chatusr', "")
    fromusr = refermsg.get('fromusr', "")
    print(f'type for chatusr is {type(chatusr)}')
    op_content = refermsg.get("content", "")
    if isinstance(chatusr, dict):
        print(f'\n\nwriting to chatusr.txt')
        
        with open("chatusr.txt", "a", encoding="utf-8") as file:
    # Write the text string to the file
            file.write(f"{refer_id}\n")
            file.write(displayname)
            file.write(f"\nfromusr: {fromusr}\n")
            file.write(f"chatusr: {chatusr}\n")
            file.write(f"title: {title}\n")
            file.write(f"refer_message: {op_content}\n")
            # json.dump(appmsg, file, indent=4) #data, txt_file, indent=4
    else:
        with open("chatusr2.txt", 'a', encoding="utf-8") as file:
            if '@chatroom' in fromusr:
                file.write('CHATROOM in FROMUSR')
            else:
                if fromusr == chatusr:
                    file.write('CHATUSR == FROMUSR')
                else:
                    file.write('WXID in FROMUSR')
            file.write(f"{refer_id} \n")
            file.write(displayname)
            file.write(f"\nfromusr: {fromusr}\n")
            file.write(f"chatusr: {chatusr}\n")
            file.write(f"title: {title}\n")
            file.write(f"refer_message: {op_content}\n")
            # json.dump(appmsg, file, indent=4)
    # print(f'contentExtractor chatusr: {chatusr}')

    # pseudo code
    # if chatusr is a dict:
        # displayname = fromusr
    # else:
        # if fromusr contains "@chatroom":
            # displayname = chatusr
        # else:
            # displayname = fromusr

    # total quoted_message 497 = 155 + 342 
    # chatusrs that are {}: 155
        # fromusr is wx_id of op
    # chatusrs that are not {}: 342 = 279 + 47 + 16 
        # fromusr contains @chatroom: 279
            # chatusr is wx_id of op
        # chatusr == fromusr: 47
            # both are wx_id of op 
        # chatusr =/= fromusr: 16 
            # wx_id depends, displayname is always op 
     

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
            'refer_id': refer_id,
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

def extract_video_post(bytes_extra: dict, compress_content: str):
    '''
    get thumbnail from bytes extra, get author and desc from compress_content
    '''
    thumbnail = None
    try:
        byest_extra_str = str(bytes_extra)
        pattern = r"b'([^']*FileStorage\\\\Cache\\\\[^']*)'"
        matches = re.findall(pattern, byest_extra_str)
        if matches:
            thumbnail = matches[0]
            thumbnail = thumbnail.replace('\\\\', '\\')

    except (KeyError, AttributeError):
        logger.error("Failed to extract thumbnail from bytes_extra")
    
    nickname, desc = None, None

    # Parse the XML
    root = ET.fromstring(compress_content)

    # Find the finderFeed element
    finder_feed = root.find(".//finderFeed")

    if finder_feed is not None:
        # Extract the nickname
        if finder_feed.find("nickname").text is not None:
            nickname = finder_feed.find("nickname").text.strip()
        # Extract the desc
        if finder_feed.find("desc").text is not None:
            desc = finder_feed.find("desc").text.strip()
    
    return {'thumbnail': thumbnail, 'author': nickname, 'desc': desc}


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
