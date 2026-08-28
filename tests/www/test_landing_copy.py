import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX = ROOT / "www" / "index.html"
STYLES = ROOT / "www" / "styles.css"

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
