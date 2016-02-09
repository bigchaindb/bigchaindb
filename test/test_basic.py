"""
A Basic Test Module
"""

import unittest

class TestBase(unittest.TestCase):
    """
    Test basic functionality
    """
    DEBUG = True  # set this flag to skip tests while debugging the unit

    @classmethod
    def setUpClass(cls):
        """
        Set up variables at TestCase-level
        """

        cls.KEY1 = 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn'
        cls.KEY2 = 'QmR9MzChjp1MdFWik7NjEjqKQMzVmBkdK3dz14A6B5Cupm'
        cls.NODE = {'Data': b'Hello World'}

    def setUp(self):
        """
        Set up variables at test-level
        """
        pass

    @unittest.skipIf(DEBUG, "debug")
    def test_one(self):
        """
        Minimal functional test
        """
        pass

if __name__ == '__main__':
    unittest.main()
