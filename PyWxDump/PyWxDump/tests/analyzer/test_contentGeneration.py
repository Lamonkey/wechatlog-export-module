import unittest
from pywxdump.analyzer import contentGeneration as CG
import os
import shutil
import json


class TestUtils(unittest.TestCase):
    json_file_path = os.path.join(
        os.path.dirname(__file__), 'valid_msg_example.json')
    save_to = os.path.join(os.path.dirname(__file__), 'output_folder')
    wechat_path = 'C:\\Users\\jianl\\Documents\\WeChat Files\\a38655162'

    def setUp(self):
        # place here so can be modified in test cases
        with open(self.json_file_path, 'r') as f:
            self.name2entry = json.load(f)

        if not os.path.exists(self.save_to):
            os.makedirs(self.save_to)

    def tearDown(self):
        if os.path.exists(self.save_to):
            shutil.rmtree(self.save_to)

    def test_add_text_content(self):
        pass

    def test_get_img_description_1(self):
        '''test with a local running_record image

        '''
        img = os.path.join(os.path.dirname(__file__),
                           'img_sources/running_record.jpg')
        description = CG._get_img_description(img)
        self.assertIsNotNone(description)
        self.assertIsInstance(description, str)
        print(description)

    def test_get_img_description_2(self):
        '''test with a local scenery image

        '''
        img = os.path.join(os.path.dirname(__file__),
                           'img_sources/scenery.jpg')
        description = CG._get_img_description(img)
        self.assertIsNotNone(description)
        self.assertIsInstance(description, str)
        print(description)
    
    def test_get_img_description_3(self):
        '''test with a url
        
        '''
        url = 'http://mmbiz.qpic.cn/mmemoticon/ajNVdqHZLLALxSLBT9ia2YE2dtWvdkSFiaqO7hG8rVPxOCPEJQF8vTCz1fU6K2NkkE/0'
        description = CG._get_img_description(url)
        self.assertIsNotNone(description)
        self.assertIsInstance(description, str)
        print(description)

    def test_invalid_encrypted_img(self):
        invalid_img_entry = self.name2entry['img_entry']
        invalid_img_entry['content']['src'] = 'invalid_path'
        with self.assertRaises(FileNotFoundError):
            CG.add_image_content(invalid_img_entry,
                                 self.wechat_path,
                                 self.save_to)

    def test_add_image_without_abs_path(self):
        save_to = "./output_folder"
        with self.assertRaises(ValueError):
            CG.add_image_content(self.name2entry['img_entry'],
                                 self.wechat_path,
                                 save_to)

    def test_add_image_content(self):
        content = CG.add_image_content(self.name2entry['img_entry'],
                                       self.wechat_path,
                                       self.save_to)
        decrypted_img = content.get('decrypted_img')
        self.assertIsNotNone(decrypted_img)
        self.assertTrue(os.path.exists(
            os.path.join(self.save_to,
                         decrypted_img)
        ))

    def test_add_audio_content(self):
        content = CG.add_audio_content(self.name2entry['audio'],
                                       self.wechat_path,
                                       self.save_to)
        audio_path = content.get('audio_path')
        transcription = content.get('transcription')
        self.assertIsNotNone(transcription)
        self.assertIsNotNone(audio_path)
        self.assertTrue(os.path.exists(
            os.path.join(self.save_to,
                         audio_path)
        ))
        
    def test_addcardlike_content(self):
        content = CG.add_cardlike_content(self.name2entry['cardlike'])
        self.assertIsNotNone(content['url'])
        self.assertIsNotNone(content['author'])
        self.assertIsNotNone(content['display_title'])
        self.assertIsNotNone(content['displayed_description'])
        self.assertIsNotNone(content['summary'])
        print(content)
    
    def test_add_emoji_content(self):
        content = CG.add_emoji_content(self.name2entry['emoji'])
        self.assertIsNotNone(content['url'])
        self.assertIsNotNone(content['description'])

    def test_add_quoted_msg_content(self):
        content = CG.add_quoted_msg_content(self.name2entry['quoted_msg'])
        self.assertEqual(content['type'], 'quoted_msg')
        pass
    
    def test_get_audio_clip(self):
        audio_path = os.path.join(self.wechat_path, 'Audio', 'audio.silk')
        self.assertTrue(os.path.exists(audio_path))
    def test_add_video_content(self):
        pass

    def test_add_file_content(self):
        pass

    def test_add_location_content(self):
        content = CG.add_location_content(self.name2entry['location'])
        self.assertIsNotNone(content)

    def test_get_audio_clip():
        pass

if __name__ == '__main__':
    unittest.main()
