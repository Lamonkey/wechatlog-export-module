import unittest
import os
import logging
from wechatlog.textualization import Textualization

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestTextualization(unittest.TestCase):

    def setUp(self):
        # Get API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.skipTest("OPENAI_API_KEY environment variable not set")
        self.textualization = Textualization(api_key)

    def test_textualize_img_url(self):
        url = "https://example.com/path/to/image.jpg"
        result = self.textualization.textualize_img(url)
        self.assertIsNotNone(result)
        logger.info(f"URL image description: {result}")

    def test_textualize_img_local(self):
        local_path = "/path/to/local/image.jpg"
        if not os.path.exists(local_path):
            self.skipTest(f"Local image not found: {local_path}")
        result = self.textualization.textualize_img(local_path)
        self.assertIsNotNone(result)
        logger.info(f"Local image description: {result}")

if __name__ == '__main__':
    unittest.main()
