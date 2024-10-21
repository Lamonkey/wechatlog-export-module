import os
import textwrap
import argparse
from pywxdump.analyzer import contentGeneration as cg
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor
from patches import contact_patch, retrieve_op_wxid


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
        sql = (
            "INSERT INTO WL_MSG (MsgSvrID, type_name, is_sender, talker, room_name, description ,content, whom, CreateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        # mentioned_user is wxid, used get method here as the safe approach in case the key doesnt exist
        whoms = msg.get('mentioned_user', [])
        content_str = None
        try:
            content = cg.get_content_by_type(
                msg, wx_root, save_to, vision_api_key, path_to_merge_db, open_ai_api_key)
            content_str = str(content)
        except Exception as e:
            print(f"{msg['MsgSvrID']} encountered issue: {e}")

        # Append room_name if not a chatroom
        if 'chatroom' not in msg['room_name']:
            whoms.append(msg['room_name'])

        # Append reply_to if is quote_msg
        if msg['type_name'] == '带有引用的文本消息':
            # op_wxid has this format [('wxid_7w175a1xeilw11',)]
            op_wxid = retrieve_op_wxid(db_parser, content['op_id'])
            if not op_wxid:
                whoms.append('unkown')
            else:
                whoms.append(op_wxid[0][0])
        print(f"Processing {msg['MsgSvrID']}")

        params = (msg["MsgSvrID"], msg["type_name"], msg["is_sender"], msg["talker"], msg["room_name"],
                  msg['description'], content_str, " ".join(whoms), msg["CreateTime"])
        db_parser.execute_sql(sql, params)

def main():
    pass

if __name__ == "__main__":
    main()