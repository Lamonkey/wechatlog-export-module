# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         utils.py
# Description:
# Author:       xaoyaoo
# Date:         2024/01/16
# -------------------------------------------------------------------------------
import base64
import json
import logging
import os
import re
import shutil
import traceback
from .rjson import ReJson
from functools import wraps
from pywxdump.dbpreprocess.utils import dat2img

def decrpyt_img_to(encrypted_img_path, wx_path, dst):
    """
    Decrypts an encrypted image and saves it to a temporary path.

    Parameters:
    - encrypted_img_path (str): The path to the encrypted image.
    - wx_path (str): The base path where the encrypted image is stored.
        wx_path is needed to genrete the outut dirname
    - dst (str): dest to save decrepted image.

    Returns:
    - str: The path to the saved decrypted image if successful, or an error message.
    """
    original_img_path = os.path.join(wx_path, encrypted_img_path)
    if not os.path.exists(original_img_path):
        raise FileNotFoundError(f"Image path does not exist: {original_img_path}")
        
    fomt, md5, out_bytes = dat2img(original_img_path)
    img_save_path = os.path.join(dst, encrypted_img_path + "_" + ".".join([md5, fomt]))
    if not os.path.exists(os.path.dirname(img_save_path)):
        os.makedirs(os.path.dirname(img_save_path))
    with open(img_save_path, "wb") as f:
        f.write(out_bytes)
    
    return img_save_path

def read_session(session_file, wxid, arg):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {session_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return session.get(wxid, {}).get(arg, None)


def get_session_wxids(session_file):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        logging.error(f"Session file not found: {session_file}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return None
    return list(session.keys())


def save_session(session_file, wxid, arg, value):
    try:
        with open(session_file, 'r') as f:
            session = json.load(f)
    except FileNotFoundError:
        session = {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {e}")
        return False

    if wxid not in session:
        session[wxid] = {}
    if not isinstance(session[wxid], dict):
        session[wxid] = {}
    session[wxid][arg] = value
    try:
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error writing to file: {e}")
        return False
    return True


def validate_title(title):
    """
    校验文件名是否合法
    """
    rstr = r"[\/\\\:\*\?\"\<\>\|\.]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def error9999(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback_data = traceback.format_exc()
            rdata = f"{traceback_data}"
            # logging.error(rdata)
            return ReJson(9999, body=rdata)

    return wrapper


def gen_base64(path):
    # 获取文件名后缀
    extension = os.path.splitext(path)[1]
    if extension == '.js':
        start_str = 'data:text/javascript;base64,'
    elif extension == '.css':
        start_str = 'data:text/css;base64,'
    elif extension == '.html':
        start_str = 'data:text/html;base64,'
    elif extension == '.json':
        start_str = 'data:application/json;base64,'
    else:
        start_str = 'data:text/plain;base64,'

    with open(path, 'rb') as file:
        js_code = file.read()

    base64_encoded_js = base64.b64encode(js_code).decode('utf-8')
    return start_str + base64_encoded_js

def merge_folders(source, destination):
    """
    Merge contents of source folder into destination folder without overriding existing files or directories.
    raise FileNotFoundError when source or destination doesn't exist
    :param source: Source folder path (folder 'a')
    :param destination: Destination folder path (folder 'b')
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source folder {source} does not exist.")

    if not os.path.exists(destination):
        raise FileNotFoundError(f"Destination folder {destination} does not exist.")

    for root, dirs, files in os.walk(source):
        # Compute the relative path from the source folder
        relative_path = os.path.relpath(root, source)
        destination_path = os.path.join(destination, relative_path)

        # Ensure the destination path exists
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Copy files
        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_path, file)
            try:
                if not os.path.exists(destination_file):
                    shutil.copy2(source_file, destination_file)
            except PermissionError:
                logging.warning(
                    f"Permission denied when copying file: {source_file}")

        # Copy directories
        for dir in dirs:
            source_dir = os.path.join(root, dir)
            destination_dir = os.path.join(destination_path, dir)
            try:
                if not os.path.exists(destination_dir):
                    shutil.copytree(source_dir, destination_dir)
            except PermissionError:
                logging.warning(
                    f"Permission denied when copying directory: {source_dir}")
