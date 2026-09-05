import json
import unittest

from squeak.update_checker import (
    is_newer_version,
    parse_release_payload,
    version_tuple,
)


class UpdateCheckerTests(unittest.TestCase):
    def test_versions_compare_numerically(self):
        self.assertEqual(version_tuple("v1.10.2"), (1, 10, 2))
        self.assertTrue(is_newer_version("1.1.0", "1.0.9"))
        self.assertFalse(is_newer_version("v1.0.0", "1.0.0"))
        self.assertFalse(is_newer_version("0.9.9", "1.0.0"))
        with self.assertRaises(ValueError):
            version_tuple("v2.0.0-beta")

    def test_release_payload_is_parsed(self):
        payload = json.dumps(
            {
                "tag_name": "v1.2.0",
                "name": "Squeak v1.2.0",
                "body": "New scoring tools.",
                "draft": False,
                "prerelease": False,
            }
        ).encode()

        release = parse_release_payload(payload)

        self.assertEqual(release.version, "1.2.0")
        self.assertEqual(release.title, "Squeak v1.2.0")
        self.assertEqual(release.notes, "New scoring tools.")

    def test_invalid_or_unstable_releases_are_rejected(self):
        with self.assertRaises(ValueError):
            parse_release_payload(b"not json")
        with self.assertRaises(ValueError):
            parse_release_payload(
                json.dumps(
                    {
                        "tag_name": "v2.0.0-beta",
                        "draft": False,
                        "prerelease": True,
                    }
                ).encode()
            )


if __name__ == "__main__":
    unittest.main()
