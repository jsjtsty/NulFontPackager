import unittest

from subtitle import build_char_map


class SubtitleTestCase(unittest.TestCase):
    def test_build_char_map(self):
        print(build_char_map('[Sakurato] Spy x Family [26][CHS].ass'))


if __name__ == '__main__':
    unittest.main()
