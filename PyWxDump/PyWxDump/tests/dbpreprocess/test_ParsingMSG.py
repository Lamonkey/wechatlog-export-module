import os
import shutil
import unittest
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create temporary source and destination folders
        self.merge_db_path = "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db"
        self.db_parser = ParsingMSG(self.merge_db_path)
        # self.destination_folder = "C:/Users/jianl/Documents/wechatlog"
        # os.makedirs(self.source_folder, exist_ok=True)
        # os.makedirs(self.destination_folder, exist_ok=True)

        # # Create some files in the source folder
        # with open(os.path.join(self.source_folder, "file1.txt"), "w") as f:
        #     f.write("This is file 1")
        # with open(os.path.join(self.source_folder, "file2.txt"), "w") as f:
        #     f.write("This is file 2")

    # def tearDown(self):
    #     # Remove the temporary folders and files
    #     shutil.rmtree(self.source_folder)
    #     shutil.rmtree(self.destination_folder)

    def test_get_all_contact(self):
        contacts = list(self.db_parser.get_all_contact())
        self.assertTrue(len(contacts) > 0)

    def test_this_table_exist(self):
        self.assertTrue(self.db_parser.is_table_exist("MSG"))

    def test_this_table_does_not_exist(self):
        self.assertFalse(self.db_parser.is_table_exist("NOT_EXISTING_TABLE"))


if __name__ == "__main__":
    unittest.main()
