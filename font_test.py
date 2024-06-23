import unittest

from font import build_font_information


class FontTestCase(unittest.TestCase):
    def test_build_font_info(self):
        result = build_font_information(r'FZZZHUNHK.TTF')
        print(result)


if __name__ == '__main__':
    unittest.main()
