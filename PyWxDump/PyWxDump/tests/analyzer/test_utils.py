import unittest
from pywxdump.analyzer import utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ocr_contain_chsinese_and_english(self):
        img = 'C:/Users/jianl/Downloads/chinese_and_english.png'
        result = utils.get_ocr_result(img)
        print(result)
        self.assertIsNotNone(result)

    def test_ocr_only_english(self):
        img = 'C:/Users/jianl/Downloads/english.png'
        result = utils.get_ocr_result(img)
        print(result)
        self.assertIsNotNone(result)

    def test_ocr_no_text(self):
        img = 'C:/Users/jianl/Downloads/no_text.jpg'
        result = utils.get_ocr_result(img)
        print(result)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
