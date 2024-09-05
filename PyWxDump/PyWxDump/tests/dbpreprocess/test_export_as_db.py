# TODO: this class can be removed
import os
import shutil
import unittest
import textwrap
from pywxdump.analyzer import contentGeneration as cg
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor
# import pywxdump.dbpreprocess.transcripting as transcripting


class TestUtils(unittest.TestCase):
    wx_root = 'C:\\Users\\jianl\\Documents\\WeChat Files\\a38655162'
    save_to = 'C:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162'
    path_to_merge_db = 'c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db'
    vision_api_key = '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'
    open_ai_api_key = 'sk-proj-dgVgtDHPxP54DcNpiiklT3BlbkFJzKmdJVcN1nA2KYKErDYR'
  
    # TODO add token for gpt here
    def setUp(self):
        self.db_parser = parsor(self.path_to_merge_db)

    # def tearDown(self):
    #     self.db_parser.empty_WL_MSG()
        
        
    def test_export_msg_to_wl(self):
        '''
        export all msg to a WL_MSG table with specific schema
        '''
        # create table if ot exist
        sql = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='WL_MSG'"
        )
        result = self.db_parser.execute_sql(sql=sql)
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
            self.db_parser.execute_sql(sql=sql)
        msgs = self.db_parser.get_all_msgs()
        for msg in msgs:
            print(f"processing {msg['MsgSvrID']}")
            sql = (
                "INSERT INTO WL_MSG (MsgSvrID, type_name, is_sender, talker, room_name, description ,content, whom, CreateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )
            whom = msg['mentioned_user']
            content_str = None
            try:
                content = cg.get_content_by_type(msg,
                                                 self.wx_root,
                                                 self.save_to,
                                                 self.vision_api_key,
                                                 self.path_to_merge_db,
                                                 self.open_ai_api_key)
                content_str = str(content)
            except Exception as e:
                print(f"{msg['MsgSvrID']} encountered issue: {e}")
                

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
            self.db_parser.execute_sql(sql, params)

        # self.db_parser.save_msg_to_WL_MSG()
        # # check if WL_MSG table is not empty
        # self.assertTrue(self.db_parser.is_table_exist("WL_MSG"))


if __name__ == "__main__":
    unittest.main()
