# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         parsingMSG.py
# Description:
# Author:       xaoyaoo
# Date:         2024/04/15
# -------------------------------------------------------------------------------
import os
import re
import textwrap
import pandas as pd

from .dbbase import DatabaseBase
from .utils import get_md5, name2typeid, typeid2name, timestamp2str, xml2dict, match_BytesExtra
import lz4.block
import blackboxprotobuf
from . import contentExtractor as extractor
from . import descGenerator as dg


class ParsingMSG(DatabaseBase):
    _class_name = "MSG"

    def __init__(self, db_path):
        super().__init__(db_path)

    def decompress_CompressContent(self, data):
        """
        解压缩Msg：CompressContent内容
        :param data: CompressContent内容 bytes
        :return:
        """
        if data is None or not isinstance(data, bytes):
            return None
        try:
            dst = lz4.block.decompress(data, uncompressed_size=len(data) << 8)
            # 已经解码完成后，还含有0x00的部分，要删掉，要不后面ET识别的时候会报错
            dst = dst.replace(b'\x00', b'')
            uncompressed_data = dst.decode('utf-8', errors='ignore')
            return uncompressed_data
        except Exception as e:
            return data.decode('utf-8', errors='ignore')

    def get_BytesExtra(self, BytesExtra):
        if BytesExtra is None or not isinstance(BytesExtra, bytes):
            return None
        # TODO:change to  use pattern to decode protocol
        deserialize_data, message_type = blackboxprotobuf.decode_message(
            BytesExtra)
        return deserialize_data

    def msg_count(self, wxid: str = ""):
        """
        获取聊天记录数量,根据wxid获取单个联系人的聊天记录数量，不传wxid则获取所有联系人的聊天记录数量
        :param MSG_db_path: MSG.db 文件路径
        :return: 聊天记录数量列表 {wxid: chat_count}
        """
        if wxid:
            sql = f"SELECT StrTalker, COUNT(*) FROM MSG WHERE StrTalker='{wxid}';"
        else:
            sql = f"SELECT StrTalker, COUNT(*) FROM MSG GROUP BY StrTalker ORDER BY COUNT(*) DESC;"

        result = self.execute_sql(sql)
        if not result:
            return {}
        df = pd.DataFrame(result, columns=["wxid", "msg_count"])
        # # 排序
        df = df.sort_values(by="msg_count", ascending=False)
        # chat_counts ： {wxid: chat_count}
        chat_counts = df.set_index("wxid").to_dict()["msg_count"]
        return chat_counts

    def msg_count_total(self):
        """
        获取聊天记录总数
        :return: 聊天记录总数
        """
        sql = "SELECT COUNT(*) FROM MSG;"
        result = self.execute_sql(sql)
        if result and len(result) > 0:
            chat_counts = result[0][0]
            return chat_counts
        return 0

    # def room_user_list(self, selected_talker):
    #     """
    #     获取群聊中包含的所有用户列表
    #     :param MSG_db_path: MSG.db 文件路径
    #     :param selected_talker: 选中的聊天对象 wxid
    #     :return: 聊天用户列表
    #     """
    #     sql = (
    #         "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
    #         "FROM MSG WHERE StrTalker=? "
    #         "ORDER BY CreateTime ASC")
    #
    #     result1 = self.execute_sql(sql, (selected_talker,))
    #     user_list = []
    #     read_user_wx_id = []
    #     for row in result1:
    #         localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent, BytesExtra, id = row
    #         bytes_extra = self.get_BytesExtra(BytesExtra)
    #         if bytes_extra:
    #             try:
    #                 talker = bytes_extra['3'][0]['2'].decode('utf-8', errors='ignore')
    #             except:
    #                 continue
    #         if talker in read_user_wx_id:
    #             continue
    #         user = get_contact(MSG_db_path, talker)
    #         if not user:
    #             continue
    #         user_list.append(user)
    #         read_user_wx_id.append(talker)
    #     return user_list

    def transcript_audio(self, audio_file):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(
                "Audio file not found: {}".format(audio_file))
        return "This is the transcript"

    def transcript_voice_msg(self, row):
        '''
        get transcript for a single voice message
        '''
        localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent, BytesExtra, id = row
        CreateTime = timestamp2str(CreateTime)
        # TODO: find a way to dynamiclly config the base path
        base_path = "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162"
        audio_file = os.path.join(base_path, "audio", f"{StrTalker}",
                                  f"{CreateTime.replace(':', '-').replace(' ', '_')}_{IsSender}_{MsgSvrID}.wav")
        try:
            return self.transcript_audio(audio_file)
        except FileNotFoundError as e:
            print(e)
            return None

    def transcript_voice_msgs_from_ids(self, msg_ids):
        '''
        return None when doesn't exist
        '''
        # TODO: this method is not used
        sql = (
            "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM MSG WHERE MsgSvrID=? "
        )
        for id in msg_ids:
            row = self.execute_sql(sql, (id,))
            if row[0]:
                yield self.transcript_voice_msg(row[0])
            else:
                yield None

    def is_voice_msg_has_transcript(self, msg_id):
        '''
        check if a voice message has transcript
        '''
        sql = "SELECT * FROM WL_transcript WHERE MsgSvrID=(?)"
        result = self.execute_sql(sql, (msg_id,))
        return len(result) > 0

    def transcript_all_and_save_to_db(self):
        '''
        transcript all voice messages and save to db
        '''
        sql = (
            "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM MSG WHERE TYPE=? and SubType=?"
        )
        rows = self.execute_sql(sql, (34, 0))
        for row in rows:
            msg_id = row[8]
            if self.is_voice_msg_has_transcript(msg_id):
                print(f'skip {msg_id}')
                continue
            else:
                transcript = self.transcript_voice_msg(row)
                if transcript is None:
                    continue

                self.add_transcript(msg_id, transcript)

    # 单条消息处理

    def msg_detail(self, row):
        """
        获取单条消息详情,格式化输出
        """
        localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType, CreateTime, MsgSvrID, DisplayContent, CompressContent, BytesExtra, id = row
        CreateTime = timestamp2str(CreateTime)

        type_id = (Type, SubType)
        type_name = typeid2name(type_id)

        content = {"src": "", "msg": StrContent}
        description = 'no description'

        if type_id == (1, 0):  # 文本
            content = extractor.extract_text_content(StrContent)
            description = dg.text(content)

        elif type_id == (3, 0):  # 图片
            DictExtra = self.get_BytesExtra(BytesExtra)
            DictExtra_str = str(DictExtra)
            content = extractor.extract_image_content(DictExtra_str)
            description = dg.image(content)
        elif type_id == (34, 0):  # 语音
            content = extractor.extract_voice_content(StrContent,
                                                      StrTalker,
                                                      CreateTime,
                                                      IsSender,
                                                      MsgSvrID)
            description = dg.voice(content)

        elif type_id == (43, 0):  # 视频
            DictExtra = self.get_BytesExtra(BytesExtra)
            DictExtra = str(DictExtra)
            content = extractor.extract_video_content(DictExtra)
            description = dg.video(content)

        elif type_id == (47, 0):  # 动画表情
            content = extractor.extract_emoji_content(StrContent)
            description = dg.emoji(content)

        elif type_id == (49, 0):  # 文件
            DictExtra = self.get_BytesExtra(BytesExtra)
            content = extractor.extract_file_content(DictExtra)
            description = dg.file(content)

        elif type_id == (49, 19):  # 合并转发的聊天记录
            CompressContent = self.decompress_CompressContent(CompressContent)
            content = extractor.extract_forwarded_message_content(
                CompressContent)
            description = dg.forwarded_message(content)

        elif type_id == (49, 57):  # 带有引用的文本消息
            CompressContent = self.decompress_CompressContent(CompressContent)
            content = extractor.extract_quoted_message_content(CompressContent)
            # get referce id
            ref_id = content.get('refer_id', -1)
            # get referece entity of msg
            ref_msg = self.get_WL_MSG_by_id(ref_id)
            # add description of ref msg to content
            if ref_msg:
                content['ref_desc'] = ref_msg.get(
                    'description', 'no description for this message')
            else:
                content['ref_desc'] = 'no description for this message'
            description = dg.quoted_message(content)

        elif type_id == (49, 2000):  # 转账消息
            CompressContent = self.decompress_CompressContent(CompressContent)
            content = extractor.extract_transfer_content(CompressContent)
            description = dg.transfer(content)

        # card-like link
        elif type_id == (49, 5):
            xml_str = self.decompress_CompressContent(CompressContent)
            content = extractor.extract_card_content(xml_str)
            description = dg.card(content)

        # TODO: 推荐公众号, the xml contain
        elif type_id == (42, 0):
            xml_dict = xml2dict(StrContent)
            for k, v in xml_dict.items():
                content[k] = v
            description = dg.contact_card(content)

        elif type_id[0] == 49 and type_id[1] != 0:
            DictExtra = self.get_BytesExtra(BytesExtra)
            content = extractor.extract_other_type_content(
                DictExtra, type_name)
            description = dg.other_type(content)

        elif type_id == (50, 0):  # 语音通话
            content = extractor.extract_call_content(DisplayContent)
            description = dg.audio_call(content)

        # elif type_id == (10000, 0):
        #     content["msg"] = StrContent
        # elif type_id == (10000, 4):
        #     content["msg"] = StrContent
        # elif type_id == (10000, 8000):
        #     content["msg"] = StrContent

        talker = extractor.get_talker(IsSender,
                                      StrTalker,
                                      self.get_BytesExtra(BytesExtra),
                                      BytesExtra)
        if MsgSvrID == 226507624180116620:
            print('stop')
        row_data = {"MsgSvrID": str(MsgSvrID),
                    "type_name": type_name,
                    "is_sender": IsSender,
                    "talker": talker,
                    "room_name": StrTalker,
                    "content": content,
                    "CreateTime": CreateTime,
                    "id": id,
                    "description": description}
        return row_data

    def get_all_msgs(self):
        '''
        return iterator of msg processed by msg_detail
        '''
        sql = (
            "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
            "FROM MSG"
        )
        rows = self.execute_sql(sql)
        for row in rows:
            yield self.msg_detail(row)

    def is_table_exist(self, table_name):
        sql = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        )
        result = self.execute_sql(sql, (table_name,))
        return result

    def save_msg_to_WL_MSG(self):
        '''
        export all msg to a WL_MSG table with specific schema
        '''
        # create table if ot exist
        sql = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='WL_MSG'"
        )
        result = self.execute_sql(sql)
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
                CreateTime INT
                )
            """)
            self.execute_sql(sql)
        msgs = self.get_all_msgs()
        for msg in msgs:
            sql = (
                "INSERT INTO WL_MSG (MsgSvrID, type_name, is_sender, talker, room_name, description ,content, CreateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            content_str = str(msg['content'])
            params = (msg["MsgSvrID"],
                      msg["type_name"],
                      msg["is_sender"],
                      msg["talker"],
                      msg["room_name"],
                      msg['description'],
                      content_str,
                      msg["CreateTime"])
            self.execute_sql(sql, params)

    def get_msg_from_WL_MSG(self):
        '''
        return iterator of msg from MSG
        '''
        sql = (
            "SELECT * FROM WL_MSG"
        )

    def get_WL_MSG_by_id(self, msg_id):
        '''
        Retrieve a single message by its ID from the WL_MSG table.
        '''
        if msg_id == -1:
            return None
        sql = "SELECT * FROM WL_MSG WHERE MsgSvrID = ?"
        result = self.execute_sql(sql, (msg_id,))
        if not result:
            return None
        keys = ['MsgSvrID', 'type_name', 'is_sender', 'talker',
                'room_name', 'description', 'content', 'CreateTime']
        message_data = tuple(field.decode(
            'utf-8') if isinstance(field, bytes) else field for field in result[0])
        return dict(zip(keys, message_data))

    def empty_WL_MSG(self):
        '''
        empty WL_MSG table
        '''
        sql = (
            "DELETE FROM WL_MSG"
        )
        self.execute_sql(sql)

    def msg_list(self, wxid="", start_index=0, page_size=500, msg_type: str = ""):
        if wxid:
            sql = (
                "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
                "FROM MSG WHERE StrTalker=? "
                "ORDER BY CreateTime ASC LIMIT ?,?")
            if msg_type:
                sql = sql.replace("ORDER BY CreateTime ASC LIMIT ?,?",
                                  f"AND Type={msg_type} ORDER BY CreateTime ASC LIMIT ?,?")
            result1 = self.execute_sql(sql, (wxid, start_index, page_size))
        else:
            sql = (
                "SELECT localId, IsSender, StrContent, StrTalker, Sequence, Type, SubType,CreateTime,MsgSvrID,DisplayContent,CompressContent,BytesExtra,ROW_NUMBER() OVER (ORDER BY CreateTime ASC) AS id "
                "FROM MSG ORDER BY CreateTime ASC LIMIT ?,?")
            if msg_type:
                sql = sql.replace("ORDER BY CreateTime ASC LIMIT ?,?",
                                  f"AND Type={msg_type} ORDER BY CreateTime ASC LIMIT ?,?")
            result1 = self.execute_sql(sql, (start_index, page_size))
        if not result1:
            return [], []
        data = []
        wxid_list = []
        for row in result1:
            tmpdata = self.msg_detail(row)
            wxid_list.append(tmpdata["talker"])
            data.append(tmpdata)
        wxid_list = list(set(wxid_list))
        return data, wxid_list

    def get_all_contact(self):
        """
        return desc sorted contact list from MSG table
        """
        sql = " ".join([
            "SELECT strTalker,MAX(CreateTime) AS lastTime",
            "from MSG",
            "GROUP BY strTalker",
            "ORDER BY lastTime DESC;"]
        )
        result = self.execute_sql(sql)
        if not result:
            return []
        return (row[0] for row in result)

    def add_transcript(self, msg_id, transcript):
        '''
        add transcript to msg_id. If the WL_transcript table doesn't exist, create it.
        '''
        insert_sql = "INSERT INTO WL_transcript (MsgSvrID, transcription) VALUES (?, ?)"

        try:
            # Execute the SQL query with msg_id and transcript as parameters
            self.execute_sql(insert_sql, (msg_id, transcript))
            print("Transcript added successfully.")
        except Exception as e:
            # Handle any errors that occur during the database operation
            print(f"An error occurred: {e}")

    def delete_transcript(self, msg_ids: list):
        '''
        remove all transcript with id in msg_ids
        '''
        deletion_sql = "DELETE FROM WL_transcript WHERE MsgSvrID=(?)"
        for id in msg_ids:
            params = (id,)
            self.execute_sql(deletion_sql, params)

    def get_transcript(self, msg_ids=None, start_datetime=None, end_datetime=None):
        '''
        get transcript with msg_ids, and between start_datetime and end_datetime.
        if msg_ids is empty list return None,
        if msg_ids is None return all,
        if start_datetime is None return all before end,
        if end_datetime is None return all after start_datetime,
        '''
        sql_parts = ["SELECT * FROM WL_transcript"]
        conditions = []

        if msg_ids is not None:
            placeholders = ', '.join(['?'] * len(msg_ids))
            conditions.append(f"MsgSvrID IN ({placeholders})")

        if start_datetime is not None:
            conditions.append("CreateTime >= ?")

        if end_datetime is not None:
            conditions.append("CreateTime <= ?")

        if conditions:
            sql_parts.append("WHERE " + " AND ".join(conditions))

        sql = " ".join(sql_parts)

        params = []
        if msg_ids is not None:
            params.extend(msg_ids)
        if start_datetime is not None:
            params.append(start_datetime)
        if end_datetime is not None:
            params.append(end_datetime)

        result = self.execute_sql(sql, params)

        return result
