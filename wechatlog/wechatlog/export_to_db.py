import textwrap
from pywxdump.analyzer import contentGeneration as cg
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor
from wechatlog import patches
from tqdm import tqdm


def execute_sql_safely(db_parser, sql, params=None):
    sql = "INSERT OR REPLACE INTO WL_MSG VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    try:
        db_parser.execute_sql(sql, params)
    except Exception as e:
        print(f"Error executing SQL: {e}")
        print(f"SQL: {sql}")
        print(f"Params: {params}")
        # Optionally, you can re-raise the exception if you want to halt execution
        # raise


def create_wl_msg_table_if_not_exists(db_parser):
    # Drop the table if it exists
    drop_table_sql = "DROP TABLE IF EXISTS WL_MSG"
    db_parser.execute_sql(sql=drop_table_sql)

    # Create the table
    create_table_sql = textwrap.dedent("""\
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
    db_parser.execute_sql(sql=create_table_sql)


def save_msg_to_db(db_parser, msg):
    sql = "INSERT OR REPLACE INTO WL_MSG VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = (
        msg["MsgSvrID"],
        msg["type_name"],
        msg["is_sender"],
        msg["talker"],
        msg["room_name"],
        msg['description'],
        msg['content_str'],
        msg['whom'],
        msg["CreateTime"]
    )
    execute_sql_safely(db_parser, sql, params)


def get_whom(msg, db_parser, content):
    whom = [decode_user(user) for user in msg.get('mentioned_user', [])]

    # Append room_name if not a chatroom
    if 'chatroom' not in msg['room_name']:
        whom.append(msg['room_name'])

    # Append reply_to if is quote_msg
    if msg['type_name'] == '带有引用的文本消息':
        # op_wxid has this format [('wxid_7w175a1xeilw11',)]
        op_wxid = patches.retrieve_op_wxid(db_parser, content['op_id'])
        if not op_wxid:
            whom.append('unknown')
        else:
            whom.append(op_wxid[0][0])

    return whom


def export_msg_to_wl(db_parser, wx_root, save_to, path_to_merge_db, progress_callback=None):
    '''
    Export all messages to a WL_MSG table with a specific schema
    '''
    msgs = db_parser.get_all_msgs()
    
    for msg in msgs:
        content_str = None
        content = None
        try:
            content = cg.get_content_by_type(
                msg=msg,
                wx_root=wx_root,
                save_to=save_to,
                path_to_merge_db=path_to_merge_db)
            content_str = str(content)
        except Exception as e:
            print(f"{msg['MsgSvrID']} encountered issue: {e}")

        whom = get_whom(msg, db_parser, content)
        
        # Add content_str and whom to msg dictionary
        msg['content_str'] = content_str
        msg['whom'] = " ".join(whom)

        save_msg_to_db(db_parser, msg)

        if progress_callback:
            progress_callback()


def decode_user(user):
    if isinstance(user, bytes):
        return user.decode('utf-8', errors='replace')
    return str(user)


if __name__ == '__main__':
    path_to_merge_db = r"c:\Users\88the\OneDrive\Desktop\wechatlog-export-module\test_output\merge_all.db"
    wx_root = r"C:\Ussd  ers\88the\OneDrive\Documents\WeChat Files\a38655162"
    output_dir = r"c:\Users\88the\OneDrive\Desktop\wechatlog-export-module\test_output"
    db_parser = parsor(path_to_merge_db)
    create_wl_msg_table_if_not_exists(db_parser)

    # Get total number of messages
    total_msgs = db_parser.msg_count_total()

    # Create a tqdm progress bar
    pbar = tqdm(total=total_msgs, desc="Exporting messages")

    # Define the progress callback function
    def update_progress():
        pbar.update(1)

    # Call export_msg_to_wl with the progress callback
    export_msg_to_wl(db_parser,
                     wx_root,
                     output_dir,
                     path_to_merge_db,
                     progress_callback=update_progress)

    # Close the progress bar
    pbar.close()

    patches.contact_patch(db_parser)
    patches.update_wechat_system_talker(db_parser)
    patches.update_self_talker(db_parser, wxid)
