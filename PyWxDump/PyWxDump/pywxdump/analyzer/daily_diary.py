from pywxdump.dbpreprocess.dbbase import DatabaseBase
from pywxdump.dbpreprocess import wxid2userinfo
import os
from datetime import datetime, timedelta

'''
generate a diary
'''

db_path = os.path.join(os.path.expanduser("~"),
                       "Downloads",
                       "pywxdumpv3027",
                       "wxdump_tmp",
                       "a38655162",
                       "merge_all.db")
db = DatabaseBase(db_path)


def get_talker_name(db_path, wxid, is_sender):
    if is_sender:
        return 'me'
    talker_name = wxid2userinfo(db_path, None, wxid)
    if not talker_name:
        return wxid
    elif talker_name[wxid]['nickname']:
        return talker_name[wxid]['nickname']
    else:
        return talker_name[wxid]['account']


def generate_diary(date):
    query_date = datetime.strptime(date, "%Y-%m-%d")
    two_day_ago = query_date - timedelta(days=2)
    query = "SELECT * FROM WL_MSG WHERE CreateTime >= ? AND CreateTime <= ? ORDER BY CreateTime DESC"
    results = db.execute_sql(query, (two_day_ago, query_date))
    text_logs = []
    for result in results:
        id, type_name, is_sender, talker, room_name, description, content, create_time = result
        talker = get_talker_name(db_path, talker, is_sender)
        room_name = get_talker_name(db_path, room_name, False)
        if 'chat' in room_name:
            log = f'at {create_time} {talker} send {description} in {room_name}'
        else:
            log = f'at {create_time} {talker} send {description} to {room_name}'
        text_logs.append(log)

    return "\n".join(text_logs)


if __name__ == "__main__":
    print(generate_diary("2024-07-01"))
    # print(get_talker_name(db_path, "20461543530@chatroom", False))
