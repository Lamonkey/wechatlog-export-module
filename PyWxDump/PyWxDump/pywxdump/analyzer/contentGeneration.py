"""
adding more content to content attribute for each type of message
"""
from pywxdump.api import utils
from pywxdump.dbpreprocess.utils import silk2audio
from pywxdump.dbpreprocess.parsingMediaMSG import ParsingMediaMSG
import os


def add_image_content(msg, wechat_path, save_to):
    '''
    return new content with decrypted img path to attribute
    input message with content filed

    save_to need to be an absolute path
    '''
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")

    content = msg['content'].copy()

    content['decrypted_img'] = utils.decrpyt_img_to(
        msg['content']['src'],
        wechat_path,
        save_to
    )
    return content


def add_audio_content(msg, wechat_path, save_to):
    '''
    return new content with path to the wav audio file
    '''
    if not os.path.isabs(save_to):
        raise ValueError("save_to must be an absolute path")
    content = msg['content'].copy()
    path = os.path.join(save_to, msg['content']['src'])
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # TODO: remove this hard coded path_to_merge_db, consider create a singleton for this class
    path_to_merge_db = 'c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db'
    pcm_data = ParsingMediaMSG(path_to_merge_db)\
        .get_audio(msg['MsgSvrID'],
                   is_play=False,
                   is_wave=True,
                   save_path=path,
                   rate=24000)
    content['audio_path'] = path
    return content
