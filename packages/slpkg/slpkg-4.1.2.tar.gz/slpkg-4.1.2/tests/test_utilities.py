import unittest
from slpkg.utilities import Utilities
from slpkg.configs import Configs


class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.utils = Utilities()
        self.build_path = Configs.build_path

    def test_build_tag(self):
        self.assertEqual(['2'], self.utils.build_tag(self.build_path,
                                                     'fish'))

    def test_ins_installed(self):
        self.assertEqual(True, self.utils.is_installed('fish-3.4.0'))


if __name__ == '__main__':
    unittest.main()
