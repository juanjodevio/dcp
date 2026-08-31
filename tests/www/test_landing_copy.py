import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX = ROOT / "www" / "index.html"
STYLES = ROOT / "www" / "styles.css"
PRIMARY_CTA_HREF = 'href="https://github.com/juanjodevio/dcp"'

REQUIRED = (
    "dcp",
    "dbt Core",
    "Elementary",
    "Docker Compose",
    "self-host",
    "https://github.com/juanjodevio/dcp",
)

BANNED = (
    "sign up",
    "pricing",
    "start free",
    "open app",
)


class LandingCopyTests(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(INDEX.is_file(), f"missing {INDEX}")

    def test_styles_exist_and_are_linked(self):
        self.assertTrue(STYLES.is_file(), f"missing {STYLES}")
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn("styles.css", html)

    def test_required_copy(self):
        html = INDEX.read_text(encoding="utf-8")
        for needle in REQUIRED:
            with self.subTest(needle=needle):
                self.assertIn(needle, html)

    def test_no_saas_cta(self):
        html = INDEX.read_text(encoding="utf-8").lower()
        for banned in BANNED:
            with self.subTest(banned=banned):
                self.assertNotIn(banned, html)

    def test_skip_link_and_main(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="#main"', html)
        self.assertIn('id="main"', html)

    def test_primary_cta_href(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn(PRIMARY_CTA_HREF, html)

    def test_referenced_assets_exist(self):
        html = INDEX.read_text(encoding="utf-8")
        css = STYLES.read_text(encoding="utf-8")
        www = ROOT / "www"
        images = re.findall(r'(?:src|srcset)="(img/[^"]+)"', html)
        fonts = re.findall(r'url\("([^"]+\.woff2)"\)', css)
        self.assertGreaterEqual(len(images), 1, "no hero image paths in index.html")
        self.assertEqual(len(fonts), 2, f"expected two woff2 files in styles.css, got {fonts}")
        for rel in images + fonts:
            with self.subTest(rel=rel):
                self.assertTrue((www / rel).is_file(), f"missing {www / rel}")
