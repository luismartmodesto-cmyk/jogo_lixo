import unittest

from scripts.build_web import (
    remove_browserfs_sourcemap_reference,
    use_local_browserfs,
)


class WebBuildTests(unittest.TestCase):
    def test_browserfs_script_uses_the_bundled_file(self):
        html = (
            '<script src="https://pygame-web.github.io/cdn/0.9.3/'
            '/browserfs.min.js"></script>'
        )

        result = use_local_browserfs(html)

        self.assertIn('<script src="browserfs.min.js"></script>', result)
        self.assertNotIn("pygame-web.github.io/cdn/0.9.3//browserfs.min.js", result)

    def test_browserfs_template_change_fails_explicitly(self):
        with self.assertRaisesRegex(RuntimeError, "exactly one BrowserFS script tag"):
            use_local_browserfs("<html></html>")

    def test_browserfs_asset_does_not_request_missing_sourcemap(self):
        source = "window.BrowserFS = {};\n//# sourceMappingURL=browserfs.min.js.map"

        result = remove_browserfs_sourcemap_reference(source)

        self.assertEqual(result, "window.BrowserFS = {};")


if __name__ == "__main__":
    unittest.main()
