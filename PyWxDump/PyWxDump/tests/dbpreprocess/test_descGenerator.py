import os
import shutil
import unittest
from pywxdump.dbpreprocess import descGenerator as dg
# import pywxdump.dbpreprocess.transcripting as transcripting


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        # self.db_parser.empty_WL_MSG()
        pass

    # def test_extract_reply_msg(self):
    #     content = {'src': '', 'msg': '这个\n\n[引用]()🌚:<?xml version="1.0"?>\n<msg>\n\t<img aeskey="d06af8c9b54ec23a9abe272ca7a15f9b" encryver="1" cdnthumbaeskey="d06af8c9b54ec23a9abe272ca7a15f9b" cdnthumburl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" cdnthumblength="2708" cdnthumbheight="104" cdnthumbwidth="150" cdnmidheight="0" cdnmidwidth="0" cdnhdheight="0" cdnhdwidth="0" cdnmidimgurl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" length="7669" cdnbigimgurl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" hdlength="16724" md5="98fe9cf422bd8762867d7299ce12dc1b" />\n</msg>\n', 'reply_with': '这个',
    #                'reply_to': '<?xml version="1.0"?>\n<msg>\n\t<img aeskey="d06af8c9b54ec23a9abe272ca7a15f9b" encryver="1" cdnthumbaeskey="d06af8c9b54ec23a9abe272ca7a15f9b" cdnthumburl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" cdnthumblength="2708" cdnthumbheight="104" cdnthumbwidth="150" cdnmidheight="0" cdnmidwidth="0" cdnhdheight="0" cdnhdwidth="0" cdnmidimgurl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" length="7669" cdnbigimgurl="304e020100044730450201000204a38003a602030f5259020427dccdcb020461b53361042065326432626661613330323863356261663966333264373363633266663961650204011c00010201000400" hdlength="16724" md5="98fe9cf422bd8762867d7299ce12dc1b" />\n</msg>\n', 'reply_to_name': '🌚'}

    def test_contact_card(self):
        content = {'src': '', 'msg': '<msg username="Ada456" nickname="AdaIsHere" fullpy="AdaIsHere" shortpy="" alias="" imagestatus="4" scene="17" province="United States" city="United States" sign="“即刻行动" sex="2" certflag="0" certinfo="" brandIconUrl="" brandHomeUrl="" brandSubscriptConfigUrl="" brandFlags="0" regionCode="US"></msg>', 'username': 'Ada456', 'nickname': 'AdaIsHere', 'fullpy': 'AdaIsHere', 'shortpy': '', 'alias': '', 'imagestatus': '4', 'scene': '17', 'province': 'United States', 'city': 'United States', 'sign': '“即刻行动', 'sex': '2', 'certflag': '0', 'certinfo': '', 'brandIconUrl': '', 'brandHomeUrl': '', 'brandSubscriptConfigUrl': '', 'brandFlags': '0', 'regionCode': 'US'}
        description = dg.contact_card(content)
        print(description)
        self.assertTrue(False)
if __name__ == "__main__":
    unittest.main()
