"""
adding more content to content attribute for each type of message
"""
from pywxdump.api import utils
from pywxdump.dbpreprocess.parsingMediaMSG import ParsingMediaMSG
import os
import logging
import base64
import textract
from openai import OpenAI
logger = logging.getLogger(__name__)


def _encode_image(image_path):
    # TODO: factor to a utility file without leading underscore
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def _get_img_description(path_or_url: str, api_key) -> str:
    # TODO: factor to a utility file without leading underscore
    """ get an image's text description

    Returns
    -------
    None
        when openai error
        or local image not found
        url error is not handled
    str
        description of the image 
    """
    client = None
    payload = {'type': 'image_url'}

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logging.error(f"openai error: {e}")
        return None
    if path_or_url.startswith("http"):
        payload['image_url'] = {"url": path_or_url}
    else:
        try:
            base64_image = _encode_image(path_or_url)
            payload['image_url'] = {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        except FileNotFoundError as e:
            logging.error(f"local image not found: {e}")
            return None

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "give me the description of this image, if image has meaningful text in it, please include it\
                            here is an example answer:\"an image show a recipt from costco with item1, item2, item3\""

                    },
                    payload
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


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
                      api_key: str,
                      enable_gpt_vision=False,
                      ) -> dict:
    '''return content with decrypted_img, description, encrypted_img

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
        - decrypted_img: relative path of saved imag
        - decrypted_thumbnail
        - description: text description of the image
        - encrypted_img: absolute path to the encrypted image
        - 

    '''
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")
    # TODO: make sure not absolute path, \
    # becaues whole problem will break by just move to another folder
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
    description = None
    if enable_gpt_vision:
        description = _get_img_description(saved_path, api_key)
    return {
        'encrypted_img': msg['content']['src'],
        'decrypted_img': saved_path,
        'encrypted_thumbnail': msg['content']['thumbnail'],
        'decrypted_thumbnail': decrypt_thumbnail,
        'description': description,
    }


def _transcript(audio_path, api_key):
    '''transcript by openai whsiper-1 model

    Returns
    -------
    transcription: of the audio
    None: 
        - when audio not found
        - error in openai api

    '''
    client = None
    try:
        client = OpenAI(
            api_key=api_key)
    except Exception as e:
        logging.error(f"openai error: {e}")
        return None

    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription.text
    except FileNotFoundError as e:
        logging.error(f"local audio not found: {e}")
        return None


def add_audio_content(msg,
                      merge_db_path,
                      save_to,
                      api_key,
                      enable_whsiper=False):
    '''return new cotent with audio_path, transcription

    Parameters
    ----------
    msg: dict
        msg need to contain['content']['src']
    wechat_path: not used 
        path to wechat root folder
    save_to: an absolute path
        path to save the audio file

    Returns
    -------
    dict: with following keys
        - audio_path: of wav audio file
        - transcription: of the audio
    '''
    content = {}
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")
    save_at = os.path.join(save_to, msg['content']['src'])
    directory = os.path.dirname(save_at)
    if not os.path.exists(directory):
        os.makedirs(directory)
    pcm_data = ParsingMediaMSG(merge_db_path)\
        .get_audio(msg['MsgSvrID'],
                   is_play=False,
                   is_wave=True,
                   save_path=save_at,
                   rate=24000)
    transcription = None
    if enable_whsiper:
        transcription = _transcript(save_at, api_key)
    content = {
        'audio_path': save_at,
        'transcription': transcription
    }
    return content


def add_cardlike_content(msg: dict, api_key, enable_scrapper=False) -> dict:
    '''Return content with url, author, displayed_title, displayed_description, and summary.

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
        - summary (str): A summary of the card-like message.

    None: if any of the required keys are missing or
    if the scraping pipeline fails to find a summary.
    '''
    source = None
    displayed_title = None
    displayed_description = None
    summary = None

    try:
        content = msg['content']
        author = content['sourcedisplayname']
        source = content['src']
        displayed_title = content['title']
        displayed_description = content['des']
    except KeyError as e:
        logger.error(f"required key in content: {e}")
        return None

    result = {'summary': None}
    if enable_scrapper:
        from scrapegraphai.graphs import SmartScraperGraph
        # Define the configuration for the scraping pipeline
        graph_config = {
            "llm": {
                # TODO: remove before commit
                "api_key": api_key,
                "model": "gpt-3.5-turbo",
            },
            "verbose": True,
            "headless": True,
        }

        smart_scraper_graph = SmartScraperGraph(
            prompt="summerize information into chinese, put it into summary",
            source=source,
            config=graph_config
        )
        result = smart_scraper_graph.run()

    if "summary" not in result:
        logger.error("No summary found.")

    summary = result.get('summary')

    return {
        "url": source,
        "author": author,
        "displayed_title": displayed_title,
        "displayed_description": displayed_description,
        "summary": summary
    }


def add_emoji_content(msg, enable_gpt_vision=False):
    '''return content with url and description'''
    url = msg['content']['src']
    description = None
    if enable_gpt_vision:
        description = _get_img_description(url)
    return {'url': url, 'descrption': description}


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


def _get_audio_clip(video_path, output_dir=None, bitrate='32k', sample_rate=22050,):
    '''Return path to audio file of the video, with significantly smaller file size.'''
    video = VideoFileClip(video_path)
    audio_clip = video.audio
    audio_path = None
    if output_dir is None:
        audio_path = os.path.splitext(video_path)[0] + '.mp3'
    else:
        audio_path = os.path.join(output_dir, os.path.basename(video_path))
        audio_path = os.path.splitext(audio_path)[0] + '.mp3'

    # Write the audio file with specified bitrate, sample rate, and channels
    audio_clip.write_audiofile(audio_path,
                               codec='mp3',
                               bitrate=bitrate,
                               fps=sample_rate,
                               nbytes=2,
                               )

    return audio_path


def _get_video_summary(img_desc,
                       audio_transcript,
                       api_key):
    client = OpenAI(api_key=api_key)
    # TODO: create a config to adjust the model
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                "role": "system",
                "content": "create a text description of this video based on the description of the cover image and the transcript, sometime either one of them will be empty. no need to mention the cover image and the transcript:"
            },
            {
                "role": "user",
                "content": f"Cover Description: {img_desc}\n\
                        Audio Transcript: {audio_transcript}"
            }
        ]
    )
    summary = response.choices[0].message.content.strip()

    return summary


def add_video_content(msg,
                      wx_root,
                      api_key,
                      enable_cover_description=False,
                      enable_video_description=False):
    '''return content with cover_img, video, summary

    upstream have issue getting the video path consistantly, sometime it will be 
    an image path, sometime it will be a video path.

    to acoomendate this bug, we will use img description or audio transcription,
    later will change to using both.

    Parameters
    ----------
    msg: dict
        msg need to contain msg['content']['src']
        - src: relative path to video, sometime its an image sometime its an video

    Returns
    -------
    dict
        content with cover_img, video, summary
        - cover_img: relative path of cover_img, None if cover_img not found
        - video: relative path of saved video, None if video not found
        - summary: text description of the cover_img or video

    '''
    cover_img, video = None, None
    if msg['content']['src'].endswith('.mp4'):
        video = msg['content']['src']
    else:
        cover_img = msg['content']['src']

    img_desc, transcription = None, None
    if cover_img and enable_cover_description:
        img_desc = _get_img_description(
            os.path.join(wx_root, cover_img), api_key)
    if video and enable_video_description:
        from moviepy.editor import VideoFileClip
        audio_clip = _get_audio_clip(os.path.join(wx_root, video))
        transcription = _transcript(audio_clip)
    description = _get_video_summary(img_desc, transcription, api_key)
    return {
        'cover_img': cover_img,
        'video': video,
        'summary': description
    }


def _extract_text(file_path):
    '''Return the text extracted from the file.

    Parameters
    ----------
    file_path : str
        The path to the file.

    Returns
    -------
    str
        The text extracted from the file.

    None
        either lack of dependence or file not found
    '''
    if not os.path.exists(file_path):
        logging.error(f'{file_path} not exist')
        return None
    try:
        text = textract.process(file_path).decode('utf-8')
    except FileNotFoundError:
        basename = os.path.basename(file_path)
        logging.error(f'the type {basename} is not supported download')
        return None

    return text


def add_file_content(msg,
                     wx_root,
                     api_key,
                     word_limit=2000,
                     enable_file_summary=False):
    '''Return content with file_path and summary.

    only text content been summariezed, chart, picture and other content
    will be ignored

    Parameters
    ----------
    msg : dict
        A dictionary containing the message details. It must include the key ['content']['src'].

    Returns
    -------
    dict
        A dictionary with the following keys:
        - file_path (str): The path to the file.
        - summary (str): The summary of the file content.
    '''
    file_path = msg['content']['src']
    file_text = _extract_text(os.path.join(wx_root, file_path))
    summary = None
    if enable_file_summary:
        words = file_text.split()
        clipped_text = " ".join(words[:word_limit])
        file_name = os.path.basename(file_path)
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            # TODO: change to config from a configuration file
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "summary the attachement from the provided file name and content just give me a general ideal what this is about"},
                {"role": "user", "content": f"filename:{file_name} content:{clipped_text}"}
            ]
        )
        summary = response.choices[0].message.content
    return {
        'file_path': file_path,
        'summary': summary
    }


def add_location_content(msg):
    '''return content with raw

    only contain raw information of this location message
    '''
    raw = msg['content']['msg']
    return {'raw': raw}


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
                                 save_to,
                                 api_key=vision_api_key,
                                 enable_gpt_vision=False)
    elif type_name == '带有引用的文本消息':
        return add_quoted_msg_content(msg)
    elif type_name == '文件':
        return add_file_content(msg,
                                wx_root,
                                open_ai_api_key)
    elif type_name == '动画表情':
        return add_emoji_content(msg)
    elif type_name == '语音':
        return add_audio_content(msg,
                                 path_to_merge_db,
                                 save_to,
                                 open_ai_api_key)
    elif type_name == '卡片式链接':
        return add_cardlike_content(msg,
                                    open_ai_api_key
                                    )
    elif type_name == '视频':
        return add_video_content(msg,
                                 wx_root,
                                 open_ai_api_key
                                 )
    else:
        return msg['content']
