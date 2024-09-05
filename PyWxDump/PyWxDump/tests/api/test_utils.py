import os
import shutil
import unittest
import pywxdump.api.utils as utils
import os


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.source_folder = os.path.join(os.getcwd(), "source_folder")
        self.destination_folder = os.path.join(os.getcwd(), "dest_folder")
        if not os.path.exists(self.source_folder):
            os.makedirs(self.source_folder)
        if not os.path.exists(self.destination_folder):
            os.makedirs(self.destination_folder)

    def tearDown(self):
        shutil.rmtree(self.source_folder)
        shutil.rmtree(self.destination_folder)

    def test_merge_folders(self):
        # Create some files in the source folder
        with open(os.path.join(self.source_folder, "file1.txt"), "w") as f:
            f.write("This is file 1")
        with open(os.path.join(self.source_folder, "file2.txt"), "w") as f:
            f.write("This is file 2")

        # Call the merge_folders function
        utils.merge_folders(self.source_folder, self.destination_folder)

        # Check if the files are successfully merged
        self.assertTrue(os.path.exists(os.path.join(
            self.destination_folder, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(
            self.destination_folder, "file2.txt")))

    def test_decrypt_image(self):
        '''
        I put the decrypted image to destination folder so it can be cleared by tearDown
        '''
        encrypted_img_path = 'FileStorage/MsgAttach/2e814e41d6151bc9c60d3aafeb3a182a/Image/2024-07/4abe916bdc3ce46e015ee1b3873113a5.dat'
        wx_path = 'C:\\Users\\jianl\\Documents\\WeChat Files\\a38655162'
        dst = self.destination_folder
        img_save_path = utils.decrpyt_img_to(encrypted_img_path, wx_path, dst)
        self.assertTrue(os.path.exists(img_save_path))


if __name__ == "__main__":
    unittest.main()
