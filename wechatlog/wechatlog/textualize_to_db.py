import os
from dotenv import load_dotenv
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG
from textualization import Textualization

# Load environment variables
load_dotenv()

# TODO: add user input later
db_path = r'c:\Users\harry\Desktop\merge_all.db'
if not db_path:
    raise ValueError("db_path is empty")

db_instance = ParsingMSG(db_path)

# Initialize Textualization
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment variables")

textualization = Textualization(OPENAI_API_KEY)

def textualize_and_save_msg(msg):
    """Textualize a message and save it back to the database."""
    if msg['content'] is None:
        return  # Skip processing if content is None
    
    # if msg['textualized_content'] is not None:
    #    return

    content = eval(msg['content'])
    textualized_content = None


    if msg['type_name'] == '图片':
        img_path = content.get('decrypted_img') or content.get('decrypted_thumbnail')
        if img_path and os.path.exists(img_path):
            textualized_content = textualization.textualize_img(img_path)
    elif msg['type_name'] == '语音':
        textualized_content = textualization.textualize_audio(content['audio_path'])
    elif msg['type_name'] == '视频':
        textualized_content = textualization.textualize_video(content.get('thumb_path'), content['video_path'])
    elif msg['type_name'] == '文件':
        textualized_content = textualization.textualize_file(content['file_path'])
    elif msg['type_name'] == '卡片式链接':
        textualized_content = textualization.textualize_cardlike(
            url=content.get('url'),
            content_author=content.get('author'),
            source=content.get('source'),
            displayed_title=content.get('title'),
            displayed_description=content.get('description')
        )
    
    if textualized_content:
        # Update the message content with the textualized version
        msg['textualized_content'] = textualized_content
        
        # Save the updated message back to the database
        db_instance.update_msg_textualized_content(msg['MsgSvrID'], textualized_content)

def process_messages():
    """Process all messages, textualize if necessary, and save back to the database."""
    msgs = db_instance.get_all_msgs_from_wl_msg()
    target_chatroom = "26582513605@chatroom"

    for msg in msgs:
        if msg['room_name'] != target_chatroom:
            continue

        if msg['type_name'] in ['图片', '语音', '视频', '文件', '链接']:
            textualize_and_save_msg(msg)

if __name__ == '__main__':
    # Ensure the WL_MSG table exists and is populated
    # export_all_to_wl_msg()
    
    # Process and textualize messages
    process_messages()

    print("Message processing and textualization completed.")
#path_wav = 'C:/Users/harry/Downloads/wxdump_tmp/wxid_fsy5oyqm39p312/audio/26582513605@chatroom/2024-05-30_20-50-54_0_6133948979221615019.wav'

# path_wav = 'C:\\\\Users\\\\harry\\\\Downloads\\\\wxdump_tmp\\\\wxid_fsy5oyqm39p312\\audio\\26582513605@chatroom\\2024-05-30_20-50-54_0_6133948979221615019.wav'