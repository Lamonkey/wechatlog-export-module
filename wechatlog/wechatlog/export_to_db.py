import textwrap
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG
from pywxdump.analyzer import contentGeneration as cg
# TODO: remove the hard coded path to DB, move this to a config file or environment varaible
db_instance = ParsingMSG(
    "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db")


def extract_interaction(msg):
    # TODO: remove the duplicate
    interact_with = []
    interact_with += msg['mentioned_user']
    if 'chatroom' not in msg['room_name']:
        interact_with.append(msg['room_name'])
    if msg['type_name'] == '带有引用的文本消息':
        interact_with.append(msg['content']['reply_to_name'])
    return interact_with


def export_to_db(wx_root,
                 save_to,
                 path_to_merge_db,
                 vision_api_key,
                 open_ai_api_key):
    '''
    export all msg to a WL_MSG table with specific schema
    '''
    if not WL_MSG_table_exist():
        create_WL_MSG_table()
    msgs = db_instance.get_all_msgs()
    for msg in msgs:
        whom = extract_interaction(msg)
        try:
            content = cg.get_content_by_type(msg,
                                             wx_root,
                                             save_to,
                                             vision_api_key,
                                             path_to_merge_db,
                                             open_ai_api_key
                                             )
            content_str = str(content)
        except Exception as e:
            print(f"skiped{msg['MsgSvrID']} due to {e}")
            continue
        params = (msg["MsgSvrID"],
                  msg["type_name"],
                  msg["is_sender"],
                  msg["talker"],
                  msg["room_name"],
                  msg['description'],
                  content_str,
                  " ".join(whom),
                  msg["CreateTime"])
        save_msg_to_WL_MSG(msg)


def save_msg_to_WL_MSG(msg):
    '''
    doesn't check if table exist, because only want to check once before batch processing
    '''
    sql = (
        "INSERT INTO WL_MSG (MsgSvrID, type_name, is_sender, talker, room_name, description ,content, whom, CreateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    whom = msg['mentioned_user']
    content_str = str(msg['content'])
    # append room_name if not a chatroom
    if 'chatroom' not in msg['room_name']:
        whom.append(msg['room_name'])
    # append reply_to if is quote_msg
    if msg['type_name'] == '带有引用的文本消息':
        whom.append(msg['content']['reply_to_name'])

    params = (msg["MsgSvrID"],
              msg["type_name"],
              msg["is_sender"],
              msg["talker"],
              msg["room_name"],
              msg['description'],
              content_str,
              " ".join(whom),
              msg["CreateTime"])
    db_instance.execute_sql(sql, params)


def create_WL_MSG_table():
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
    db_instance.execute_sql(sql)


def WL_MSG_table_exist():
    sql = (
        "SELECT name FROM sqlite_master WHERE type='table' AND name='WL_MSG'"
    )
    result = db_instance.execute_sql(sql)
    return result


def export_all_to_wl_msg():
    '''
    export all msg to a WL_MSG table with specific schema
    '''
    if not WL_MSG_table_exist():
        create_WL_MSG_table()
    msgs = db_instance.get_all_msgs()
    for msg in msgs:
        save_msg_to_WL_MSG(msg)
