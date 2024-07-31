"""
adding more content to content attribute for each type of message
"""
from pywxdump.api import utils
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