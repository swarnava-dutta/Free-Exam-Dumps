import re
from typing import Iterable, List, Tuple
from urllib.parse import urljoin, urlparse

from .settings import BASE_URL


def normalize_slug(value: str) -> str:
    """Lowercase, alphanumerics only. Used as the comparison key everywhere."""
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def display_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


def normalize_provider(provider: str) -> str:
    """Provider slug from a name, a slug, or any examtopics URL."""
    provider = (provider or "").strip()
    if not provider:
        return ""

    parsed = urlparse(provider)
    path = (parsed.path if parsed.scheme else provider).strip("/")
    for pattern in (r"(?:^|/)discussions/([^/]+)", r"(?:^|/)exams/([^/]+)"):
        match = re.search(pattern, path, re.I)
        if match:
            return match.group(1).lower()

    # ponytail: slugify rather than lower(). A plain lower() turned "Palo Alto Networks"
    # into "palo alto networks" and built a URL that 404s, breaking every one of the
    # ~30 multi-word providers on the site.
    return display_slug(provider)


def dedupe(values: Iterable[str]) -> List[str]:
    """Order-preserving dedupe."""
    return list(dict.fromkeys(values))


def provider_discussion_url(provider: str, page_number: int = 1) -> str:
    base_url = f"{BASE_URL}/discussions/{normalize_provider(provider)}/"
    return f"{base_url}{page_number}/" if page_number > 1 else base_url


def exam_url(provider: str, exam_slug: str) -> str:
    return f"{BASE_URL}/exams/{provider}/{exam_slug}/"


def exam_match_key(exam_slug: str) -> str:
    """Anchored needle for listing entries: "exam<slug>topic".

    The trailing "topic" anchor is what stops a shorter exam slug from swallowing a
    longer one: without it "aws-certified-developer-associate" also matches every
    "aws-certified-developer-associate-dva-c02" entry.
    """
    return "exam" + normalize_slug(exam_slug) + "topic"


def matches_exam(text: str, href: str, key: str) -> bool:
    """Does a listing entry belong to the exam identified by `key`?"""
    # ponytail: link text is the primary signal, href only a backstop. examtopics
    # truncates long hrefs before the "-topic" anchor, so SAA-C03 matched 0 of its 44
    # sampled entries by href and all 44 by text.
    return key in normalize_slug(text) or key in normalize_slug(href)


def discussion_entry_url(text: str, href: str) -> str:
    """Absolute discussion URL, with the truncated listing slug rebuilt from the
    link text so the saved link is self-describing.

    Only the numeric id is load bearing; examtopics serves the right question for any
    slug after it. The rebuild is purely so a reader can see topic and question number.
    """
    absolute_url = urljoin(BASE_URL, href)
    parsed = urlparse(absolute_url)
    path_match = re.search(r"^(/discussions/[^/]+/view/)(\d+)-", parsed.path)

    if path_match and re.search(r"\btopic\s+\d+\s+question\s+\d+\b", text, re.I):
        return urljoin(
            BASE_URL, f"{path_match.group(1)}{path_match.group(2)}-{display_slug(text)}/"
        )
    return absolute_url


def extract_topic_question(link: str) -> Tuple[int, int]:
    """(topic, question) for sorting. Unparseable links sort last."""
    match = re.search(r"topic-(\d+)-question-(\d+)", link, re.I)
    if not match:
        return (10**9, 10**9)
    return (int(match.group(1)), int(match.group(2)))
