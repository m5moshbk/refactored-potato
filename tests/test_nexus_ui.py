from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MarkupAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs)

    def _record(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.tags.append((tag.lower(), values))
        if values.get("id"):
            self.ids.append(str(values["id"]))


def load_page(name: str) -> tuple[str, MarkupAudit]:
    source = (ROOT / name).read_text(encoding="utf-8")
    parser = MarkupAudit()
    parser.feed(source)
    parser.close()
    return source, parser


class NexusIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source, cls.audit = load_page("index.html")

    def test_arabic_rtl_skip_link_and_single_main_landmark(self) -> None:
        self.assertRegex(self.source, r'<html[^>]+lang="ar"[^>]+dir="rtl"')
        self.assertIn('class="skip-link" href="#main-content"', self.source)
        self.assertEqual(sum(tag == "main" for tag, _ in self.audit.tags), 1)
        self.assertTrue(any(tag == "main" and attrs.get("id") == "main-content"
                            for tag, attrs in self.audit.tags))

    def test_dom_ids_are_unique(self) -> None:
        duplicates = [name for name, count in Counter(self.audit.ids).items() if count > 1]
        self.assertEqual(duplicates, [])

    def test_all_static_buttons_have_explicit_type(self) -> None:
        buttons = [attrs for tag, attrs in self.audit.tags if tag == "button"]
        self.assertGreater(len(buttons), 20)
        self.assertTrue(all(attrs.get("type") in {"button", "submit", "reset"}
                            for attrs in buttons))

    def test_project_filters_expose_pressed_state_and_target(self) -> None:
        filters = [attrs for tag, attrs in self.audit.tags
                   if tag == "button" and "filter" in (attrs.get("class") or "").split()]
        self.assertEqual(len(filters), 4)
        self.assertTrue(all(attrs.get("aria-controls") == "grid" for attrs in filters))
        self.assertEqual({attrs.get("aria-pressed") for attrs in filters}, {"true", "false"})

    def test_search_feedback_is_announced(self) -> None:
        self.assertRegex(self.source, r'id="empty"[^>]+role="status"[^>]+aria-live="polite"')
        self.assertIn("projectResultsCount", self.source)

    def test_responsive_and_reduced_motion_rules_exist(self) -> None:
        self.assertIn("@media(max-width:800px)", self.source)
        self.assertIn("@media(max-width:520px)", self.source)
        self.assertIn("prefers-reduced-motion:reduce", self.source)
        self.assertIn(":focus-visible", self.source)

    def test_scope_statement_does_not_claim_live_health(self) -> None:
        self.assertIn("وجود الرابط لا يثبت أن الخدمة تعمل الآن", self.source)
        self.assertIn("لا يوجد فحص حي للخدمات", self.source)
        self.assertIn("© M5mOsH All Rights Reserved", self.source)

    def test_no_deploy_or_database_mutation_endpoint_was_added(self) -> None:
        self.assertNotRegex(self.source, r"fetch\s*\([^)]*/(?:deploy|restart|database|production)")
        self.assertNotRegex(self.source, r"axios\.(?:post|put|patch|delete)\s*\([^)]*/(?:deploy|restart|database|production)")

    def test_owner_repair_request_routes_to_private_reviewable_inbox(self) -> None:
        self.assertIn("m5moshbk/M5mOsH-Task-Orchestrator/issues/new", self.source)
        self.assertIn('id="nxRepairRoute"', self.source)
        self.assertIn('id="nxRepairTicketPreview"', self.source)
        self.assertIn("Create new issue", self.source)
        self.assertIn("handoff_open_requested_not_submitted", self.source)
        self.assertIn("لم تُحفظ التذكرة ولم يبدأ التنفيذ بعد", self.source)

    def test_owner_repair_handoff_blocks_common_secret_patterns(self) -> None:
        self.assertIn("const secretLike=", self.source)
        self.assertIn("github_pat_", self.source)
        self.assertIn("Bearer", self.source)
        self.assertIn("SECRET(?:_ACCESS_KEY)?", self.source)
        self.assertIn("DATABASE_URL", self.source)
        self.assertIn("PRIVATE KEY", self.source)
        self.assertIn("const rawNote=", self.source)
        self.assertIn("secretLike.test(rawNote)", self.source)
        self.assertIn("rawNote.length>600", self.source)
        self.assertIn("لن يتم اقتطاع النص بصمت", self.source)
        self.assertIn("لا تُرسل أسرارًا إلى التذكرة", self.source)


class DesignSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source, cls.audit = load_page("design-system.html")

    def test_arabic_rtl_skip_link_and_single_main_landmark(self) -> None:
        self.assertRegex(self.source, r'<html[^>]+lang="ar"[^>]+dir="rtl"')
        self.assertIn('class="skip-link" href="#main-content"', self.source)
        self.assertEqual(sum(tag == "main" for tag, _ in self.audit.tags), 1)
        self.assertTrue(any(tag == "main" and attrs.get("id") == "main-content"
                            for tag, attrs in self.audit.tags))

    def test_theme_options_have_accessible_pressed_state(self) -> None:
        themes = [attrs for tag, attrs in self.audit.tags
                  if tag == "button" and attrs.get("data-theme-choice")]
        self.assertEqual(len(themes), 4)
        self.assertEqual({attrs.get("aria-pressed") for attrs in themes}, {"true", "false"})

    def test_local_theme_persistence_is_scoped_and_validated(self) -> None:
        self.assertIn("m5mosh-nexus-design-theme-v1", self.source)
        self.assertIn("new Set(['cinematic','luxury','cyber','enterprise'])", self.source)
        self.assertIn("localStorage.setItem(themeKey,theme)", self.source)

    def test_interaction_examples_announce_local_results(self) -> None:
        self.assertIn('id="states"', self.source)
        self.assertIn('id="dsInteractionStatus"', self.source)
        self.assertIn('role="status" aria-live="polite"', self.source)
        self.assertIn("لم يتم إرسال أي طلب إلى خادم", self.source)

    def test_all_static_buttons_have_explicit_type_and_ids_are_unique(self) -> None:
        buttons = [attrs for tag, attrs in self.audit.tags if tag == "button"]
        self.assertTrue(all(attrs.get("type") in {"button", "submit", "reset"}
                            for attrs in buttons))
        duplicates = [name for name, count in Counter(self.audit.ids).items() if count > 1]
        self.assertEqual(duplicates, [])

    def test_reduced_motion_focus_and_rights_identity(self) -> None:
        self.assertIn("prefers-reduced-motion:reduce", self.source)
        self.assertIn(":focus-visible", self.source)
        self.assertIn("© M5mOsH All Rights Reserved", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
