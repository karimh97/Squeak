import unittest

from squeak import branding


class BrandingTests(unittest.TestCase):
    def test_runtime_wordmark_assets_exist(self):
        self.assertTrue(branding.LOGO_SOURCE_PATH.is_file())
        self.assertTrue(branding.LOGO_DARK_BG_PATH.is_file())
        self.assertTrue(branding.LOGO_LIGHT_BG_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
