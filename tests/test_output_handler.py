import unittest
from core.output_handler import OutputHandler

class TestOutputHandler(unittest.TestCase):

    def test_generate_filename(self):
        media_path = 'product_image_001.jpg'
        text = '限时优惠 立即抢购'
        result = OutputHandler.generate_filename(media_path, text)
        self.assertEqual(result, 'produc_限时优惠立即.jpg')

    def test_generate_filename_video(self):
        media_path = 'video_clip.avi'
        text = '新品上市'
        result = OutputHandler.generate_filename(media_path, text)
        self.assertEqual(result, 'video__新品上市.mp4')

if __name__ == '__main__':
    unittest.main()
