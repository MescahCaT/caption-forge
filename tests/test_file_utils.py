import unittest
from pathlib import Path
from utils.file_utils import is_image, is_video, get_file_extension

class TestFileUtils(unittest.TestCase):

    def test_is_image(self):
        self.assertTrue(is_image('test.jpg'))
        self.assertTrue(is_image('test.png'))
        self.assertFalse(is_image('test.mp4'))

    def test_is_video(self):
        self.assertTrue(is_video('test.mp4'))
        self.assertTrue(is_video('test.avi'))
        self.assertFalse(is_video('test.jpg'))

    def test_get_file_extension(self):
        self.assertEqual(get_file_extension('test.jpg'), '.jpg')
        self.assertEqual(get_file_extension('path/to/video.mp4'), '.mp4')

if __name__ == '__main__':
    unittest.main()
