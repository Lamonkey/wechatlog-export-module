"""
adding more content to content attribute for each type of message
"""
from pywxdump.api import utils
from pywxdump.dbpreprocess.parsingMediaMSG import ParsingMediaMSG
import os
import logging
import textract
from openai import OpenAI
import base64
from moviepy.editor import VideoFileClip
logger = logging.getLogger(__name__)


def _encode_image(image_path):
    # TODO: factor to a utility file without leading underscore
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def add_text_content(msg: dict) -> dict:
    """return content with text

    Parameters
    ----------
    msg: dict
    msg need to contain['content']['msg']

    Returns
    -------
    dict
    content with text field
    """
    content = {}
    content['text'] = msg['content']['msg']
    return content


def add_image_content(msg: dict,
                      wx_root: str,
                      save_to: str,
                      ) -> dict:
    '''return content with decrypted_img, encrypted_img

    Parameters
    ----------
    msg:
        msg need to contain['content']['src']
    wx_root:
        path to account folder under wx
    save_to:
        path to save the decrypted img

    Returns
    -------
    dict: with following keys
        - decrypted_img: relative path of saved image
        - decrypted_thumbnail
        - encrypted_img: absolute path to the encrypted image
        - encrypted_thumbnail: absolute path to the encrypted thumbnail

    '''
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")
    # TODO: make sure not absolute path, \
    # because whole problem will break by just move to another folder
    saved_path, decrypt_thumbnail = None, None
    try:
        saved_path = utils.decrpyt_img_to(
            msg['content']['src'],
            wx_root,
            save_to
        )
    except FileNotFoundError:
        logging.error(f"{msg['MsgSvrID']} doesn't have compressed img")
    try:
        decrypt_thumbnail = utils.decrpyt_img_to(
            msg['content']['thumbnail'],
            wx_root,
            save_to
        )
    except FileNotFoundError:
        logging.error(f"{msg['MsgSvrID']} doesn't have thumbnail img")
    return {
        'encrypted_img': msg['content']['src'],
        'decrypted_img': saved_path,
        'encrypted_thumbnail': msg['content']['thumbnail'],
        'decrypted_thumbnail': decrypt_thumbnail,
    }


def add_audio_content(msg,
                      merge_db_path,
                      save_to):
    '''return new cotent with audio_path

    Parameters
    ----------
    msg: dict
        msg need to contain['content']['src']
    save_to: an absolute path
        path to save the audio file

    Returns
    -------
    dict: with following keys
        - audio_path: of wav audio file
    '''
    content = {}
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")
    save_at = os.path.join(save_to, msg['content']['src'])
    directory = os.path.dirname(save_at)
    if not os.path.exists(directory):
        os.makedirs(directory)
    ParsingMediaMSG(merge_db_path).get_audio(msg['MsgSvrID'],
                                             is_play=False,
                                             is_wave=True,
                                             save_path=save_at,
                                             rate=24000)
    content = {
        'audio_path': save_at,
    }
    return content


def add_cardlike_content(msg: dict, api_key, enable_scrapper=False) -> dict:
    '''Return content with url, author, displayed_title, displayed_description.

    Parameters
    ----------
    msg : dict
        A dictionary containing content key,
        the content must include the following keys:
        - title (str): The title of the content.
        - src (str): The source URL of the content.
        - des (str): The description of the content.
        - sourcedisplayname (str): The display name of the source.

    Returns
    -------
    dict
        A dictionary with the following keys:
        - url (str): The link to the content.
        - author (str): The author of the content.
        - displayed_title (str): The title when displayed in WeChat.
        - displayed_description (str): The description when displayed in WeChat.

    None: if any of the required keys are missing.
    '''
    try:
        content = msg['content']
        author = content['sourcedisplayname']
        source = content['src']
        displayed_title = content['title']
        displayed_description = content['des']
    except KeyError as e:
        logger.error(f"required key in content: {e}")
        return None

    return { 
        "url": source,
        "author": author,
        "displayed_title": displayed_title,
        "displayed_description": displayed_description,
    }


def add_emoji_content(msg, enable_gpt_vision=False):
    '''return content with url and description'''
    url = msg['content']['src']
    return {'url': url}


def add_quoted_msg_content(msg):
    '''return content with op_id, op_description, comment

    Paremters
    ---------
    msg: dict
        msg need to contain['content']['refer_id'], msg['content']['reply_with']

    Returns
    -------
    dict
        content with op, comment, op_description

    '''
    op_id = msg['content']['refer_id']
    comment = msg['content']['reply_with']
    # TODO replace with real description
    op_description = "this is a testing description"

    return {
        'op_id': op_id,
        'op_description': op_description,
        'comment': comment
    }


def add_video_content(msg, wx_root):
    '''return content with cover_img and video

    upstream have issue getting the video path consistently, sometime it will be 
    an image path, sometime it will be a video path.

    Parameters
    ----------
    msg: dict
        msg need to contain msg['content']['src']
        - src: relative path to video, sometime its an image sometime its a video
    wx_root: str
        root directory of WeChat files

    Returns
    -------
    dict
        content with cover_img and video
        - cover_img: relative path of cover_img, None if cover_img not found
        - video: relative path of saved video, None if video not found
    '''
    cover_img, video = None, None
    if msg['content']['src'].endswith('.mp4'):
        video = msg['content']['src']
    else:
        cover_img = msg['content']['src']

    return {
        'cover_img': cover_img,
        'video': video
    }


def add_file_content(msg, wx_root):
    '''Return content with file_path.

    Parameters
    ----------
    msg : dict
        A dictionary containing the message details. It must include the key ['content']['src'].
    wx_root : str
        The root directory of WeChat files.

    Returns
    -------
    dict
        A dictionary with the following key:
        - file_path (str): The path to the file.
    '''
    file_path = msg['content']['src']
    return {
        'file_path': file_path,
    }
# Remove or comment out the following functions as they're no longer used in add_video_content
# def _get_audio_clip(video_path, output_dir=None, bitrate='32k', sample_rate=22050):
#     ...

# def _get_video_summary(img_desc, audio_transcript, api_key):
#     ...

# Update get_content_by_type function


def get_content_by_type(msg,
                        wx_root,
                        save_to,
                        vision_api_key,
                        path_to_merge_db,
                        open_ai_api_key):
    type_name = msg['type_name']
    if type_name == '文本':
        return add_text_content(msg)
    elif type_name == '图片':
        return add_image_content(msg,
                                 wx_root,
                                 save_to)
    elif type_name == '带有引用的文本消息':
        return add_quoted_msg_content(msg)
    elif type_name == '文件':
        return add_file_content(msg, wx_root)
    elif type_name == '动画表情':
        return add_emoji_content(msg)
    elif type_name == '语音':
        return add_audio_content(msg,
                                 path_to_merge_db,
                                 save_to)
    elif type_name == '卡片式链接':
        return add_cardlike_content(msg,
                                    open_ai_api_key
                                    )
    elif type_name == '视频':
        return add_video_content(msg, wx_root)
    else:
        return msg['content']
