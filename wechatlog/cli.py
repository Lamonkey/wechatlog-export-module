import os
import textwrap
import argparse
from pywxdump.analyzer import contentGeneration as cg
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor

def print_ascii_art():
    art = r"""
    __        __   _                            _        
    \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
     \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
      \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
       \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
    """
    print(art)

def setup_parser():
    parser = argparse.ArgumentParser(description='Process WeChat logs and export messages.')
    parser.add_argument('--wx_root', required=True, help='Root directory of WeChat files.')
    parser.add_argument('--save_to', required=True, help='Directory to save processed files.')
    parser.add_argument('--path_to_merge_db', required=True, help='Path to the merged database.')
    parser.add_argument('--vision_api_key', required=False, help='API key for vision processing (optional).')
    parser.add_argument('--open_ai_api_key', required=False, help='API key for OpenAI (optional).')
    return parser

def export_msg_to_wl(db_parser, wx_root, save_to, path_to_merge_db, vision_api_key, open_ai_api_key):
    '''
    Export all messages to a WL_MSG table with a specific schema
    '''
    # Create table if it does not exist
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='WL_MSG'"
    result = db_parser.execute_sql(sql=sql)
    if not result:
        sql = textwrap.dedent("""\
        CREATE TABLE WL_MSG (
            MsgSvrID INTEGER PRIMARY KEY,
            type_name TEXT,
            is_sender INTEGER,
            talker TEXT,
            room_name TEXT,
            description TEXT,
            content TEXT,
            whom TEXT,
            CreateTime INT
            )
        """)
        db_parser.execute_sql(sql=sql)
        
    msgs = db_parser.get_all_msgs()
    for msg in msgs:
        print(f"Processing {msg['MsgSvrID']}")
        sql = (
            "INSERT INTO WL_MSG (MsgSvrID, type_name, is_sender, talker, room_name, description ,content, whom, CreateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        whom = msg.get('mentioned_user', [])
        content_str = None
        try:
            content = cg.get_content_by_type(msg, wx_root, save_to, vision_api_key, path_to_merge_db, open_ai_api_key)
            content_str = str(content)
        except Exception as e:
            print(f"{msg['MsgSvrID']} encountered issue: {e}")
        
        # Append room_name if not a chatroom
        if 'chatroom' not in msg['room_name']:
            whom.append(msg['room_name'])

        # Append reply_to if is quote_msg
        if msg['type_name'] == '带有引用的文本消息':
            whom.append(msg['content']['reply_to_name'])
            
        params = (msg["MsgSvrID"], msg["type_name"], msg["is_sender"], msg["talker"], msg["room_name"],
                  msg['description'], content_str, " ".join(whom), msg["CreateTime"])
        db_parser.execute_sql(sql, params)

def main():
    print_ascii_art()
    parser = setup_parser()
    args = parser.parse_args()

    # Initialize parser with provided database path
    db_parser = parsor(args.path_to_merge_db)
    
    # Process messages with the correct path to the merged database
    export_msg_to_wl(db_parser, args.wx_root, args.save_to, args.path_to_merge_db, args.vision_api_key, args.open_ai_api_key)
    print("WeChat log processing completed.")

if __name__ == "__main__":
    main()
