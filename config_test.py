import unittest

from config import read_config


class ConfigTestCase(unittest.TestCase):
    def test_read_config(self):
        result: dict = read_config('cases/config.yml')
        print(result)


if __name__ == '__main__':
    unittest.main()
