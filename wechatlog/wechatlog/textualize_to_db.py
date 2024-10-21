import os
from dotenv import load_dotenv
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG
from textualization import Textualization

def textualize_and_save_msg(db_instance, textualization, msg):
    """Textualize a message and save it back to the database."""
    textualized_content = textualization.textualize(msg)
    if textualized_content:
        # Update the message content with the textualized version
        msg['textualized_content'] = textualized_content
        # Save the updated message back to the database
        db_instance.update_msg_textualized_content(msg['MsgSvrID'], textualized_content)

def process_messages(db_instance, textualization):
    """Process all messages, textualize if necessary, and save back to the database."""
    msgs = db_instance.get_all_msgs_from_wl_msg()
    target_chatroom = "26582513605@chatroom"

    for msg in msgs:
        if msg['room_name'] != target_chatroom:
            continue

        if msg['type_name'] in ['图片', '语音', '视频', '文件', '链接']:
            textualize_and_save_msg(db_instance, textualization, msg)

def main():
    # Load environment variables
    load_dotenv()

    # TODO: add user input later
    db_path = r'c:\Users\88the\Downloads\wxdump_work\a38655162\merge_all.db'
    if not db_path:
        raise ValueError("db_path is empty")

    db_instance = ParsingMSG(db_path)

    # Initialize Textualization
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment variables")

    textualization = Textualization(OPENAI_API_KEY)

    # Process and textualize messages
    process_messages(db_instance, textualization)

    print("Message processing and textualization completed.")

if __name__ == '__main__':
    main()
