import os
import shutil
import unittest
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor
# import pywxdump.dbpreprocess.transcripting as transcripting


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create temporary source and destination folders
        self.merge_db_path = "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db"
        self.db_parser = parsor(self.merge_db_path)

    def tearDown(self):
        # self.db_parser.empty_WL_MSG()
        pass
        
    def test_export_msg_to_wl(self):
        self.db_parser.save_msg_to_WL_MSG()
        # check if WL_MSG table is not empty
        self.assertTrue(self.db_parser.is_table_exist("WL_MSG"))



if __name__ == "__main__":
    unittest.main()
