import unittest
from pywxdump.analyzer import contentGeneration as CG
import os
import shutil


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.save_to = "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\output_folder\\"
        self.img_entry = {'MsgSvrID': '7937950990010314980',
                          'type_name': '图片',
                          'is_sender': 1,
                          'talker': '我',
                          'room_name': 'qunaer001',
                          'content': {'src': 'FileStorage\\MsgAttach\\2e814e41d6151bc9c60d3aafeb3a182a\\Image\\2024-07\\a18817213ac6f0b971d2b1fc2e25fb88.dat',
                                      'msg': '图片'},
                          'CreateTime': '2024-05-08 13:19:46',
                          'id': 1890,
                          'description': 'an image',
                          'mentioned_user': []}
        self.wechat_path = 'C:\\Users\\jianl\\Documents\\WeChat Files\\a38655162'
        if not os.path.exists(self.save_to):
            os.makedirs(self.save_to)

    def tearDown(self):
        if os.path.exists(self.save_to):
            shutil.rmtree(self.save_to)

    def test_invalid_encrypted_img(self):
        invalid_img_entry = self.img_entry
        invalid_img_entry['content']['src'] = 'invalid_path'
        with self.assertRaises(FileNotFoundError):
            CG.add_image_content(invalid_img_entry,
                                 self.wechat_path,
                                 self.save_to)


    def test_add_image_without_abs_path(self):
        save_to = "./output_folder"
        with self.assertRaises(ValueError):
            CG.add_image_content(self.img_entry,
                                 self.wechat_path,
                                 save_to)

    def test_add_image_content(self):
        content = CG.add_image_content(self.img_entry,
                                       self.wechat_path,
                                       self.save_to)
        decrypted_img = content.get('decrypted_img')
        self.assertIsNotNone(decrypted_img)
        self.assertTrue(os.path.exists(
            os.path.join(self.save_to,
                         decrypted_img)
        ))


if __name__ == '__main__':
    unittest.main()
