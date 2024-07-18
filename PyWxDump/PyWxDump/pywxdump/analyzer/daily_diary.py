import os
from datetime import datetime, timedelta
from functools import lru_cache
from pywxdump.dbpreprocess.dbbase import DatabaseBase
from pywxdump.dbpreprocess import wxid2userinfo
from openai import OpenAI

def setup_openai_api(api_key):
    return OpenAI(api_key=api_key)

def setup_database(db_path):
    return DatabaseBase(db_path)


@lru_cache(maxsize=128)
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


def get_chats_for_diary(db, db_path, date):
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


def generate_diary(text_log, client):
    system_prompt = """
You are a editor at new york time, which given a task to create a diary based on \
the chat log, the chat log most likely contain three consequtive days.\
if the text_log is empty tell user there is no chat log for this day.\
output the result in chinese.\
"""
   
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {'role':'system', "content": system_prompt},
            {'role':'user', "content": text_log}
        ]


    )
    return response.choices[0].message.content


if __name__ == "__main__":
    db_path = 'c:/Users/jianl/Downloads/pywxdumpv3027/wxdump_tmp/a38655162/merge_all.db'
    db = setup_database(db_path)
    text_log = get_chats_for_diary(db, db_path, "2024-06-19")
    print(generate_diary(text_log))
    # print(get_talker_name(db_path, "20461543530@chatroom", False))
