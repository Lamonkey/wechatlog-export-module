import unittest
from pywxdump.analyzer import contentGeneration as CG
import os
import shutil


class TestUtils(unittest.TestCase):

    def setUp(self):
        # for image
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

        # for audio
        self.audio_entry = {
            'MsgSvrID': '2149179895562747041',
            'type_name': '语音',
            'is_sender': 0,
            'talker': 'qunaer001',
            'room_name': 'qunaer001',
            'content': {'src': 'audio\\qunaer001\\2024-06-10_18-46-31_0_2149179895562747041.wav',
                        'msg': '语音时长：\\37.39秒\n        翻译结果：this is a transcription',
                        'duration': '37.39',
                        'transcription': 'this is a transcription'},
            'CreateTime': '2024-06-10 18:46:31',
            'id': 1937,
            'description': "a 37.39 seconds audio with transcription: 'this is a transcription'",
            'mentioned_user': []
        }

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

    def test_add_audio_content(self):
        content = CG.add_audio_content(self.audio_entry,
                                       self.wechat_path,
                                       self.save_to)
        audio_path = content.get('audio_path')
        self.assertIsNotNone(audio_path)
        self.assertTrue(os.path.exists(
            os.path.join(self.save_to,
                         audio_path)
        ))


if __name__ == '__main__':
    unittest.main()
