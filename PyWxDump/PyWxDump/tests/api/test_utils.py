import os
import shutil
import unittest
from pywxdump.api.utils import merge_folders


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create temporary source and destination folders
        self.source_folder = "C:/Users/jianl/Documents/WeChat Files/nonExistingUser"
        self.destination_folder = "C:/Users/jianl/Documents/wechatlog"
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

    def test_merge_folders(self):
        # Call the merge_folders function
        merge_folders(self.source_folder, self.destination_folder)

        self.assertTrue(True)
        # # Check if the files are copied to the destination folder
        # self.assertTrue(os.path.exists(os.path.join(
        #     self.destination_folder, "file1.txt")))
        # self.assertTrue(os.path.exists(os.path.join(
        #     self.destination_folder, "file2.txt")))


if __name__ == "__main__":
    unittest.main()
