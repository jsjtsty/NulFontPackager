import unittest

from font import build_font_information


class FontTestCase(unittest.TestCase):
    def test_build_font_info(self):
        result = build_font_information(r'/Volumes/T7S-Personal/ACG/Animations/Made in Abyss Movie/Fonts/SourceHanSansSC-Medium.otf')
        print(result)


if __name__ == '__main__':
    unittest.main()
