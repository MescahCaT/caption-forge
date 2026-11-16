import unittest
from utils.text_utils import split_by_double_newline, truncate_text, is_cjk_char

class TestTextUtils(unittest.TestCase):

    def test_split_by_double_newline(self):
        text = "第一段\n继续第一段\n\n第二段\n\n第三段"
        result = split_by_double_newline(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "第一段\n继续第一段")

    def test_truncate_text(self):
        text = "限时 优惠 活动"
        result = truncate_text(text, 6)
        self.assertEqual(result, "限时优惠活动")

    def test_is_cjk_char(self):
        self.assertTrue(is_cjk_char('中'))
        self.assertTrue(is_cjk_char('あ'))
        self.assertFalse(is_cjk_char('A'))

if __name__ == '__main__':
    unittest.main()
