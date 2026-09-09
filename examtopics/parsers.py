import json
import re
from html import unescape
from typing import Dict, List, Tuple
from urllib.parse import urljoin

from .settings import BASE_URL

# ponytail: regex, not an HTML parser. Every selector below is a single stable class
# or data attribute, and the lookahead form makes attribute order irrelevant, so a
# parser dependency buys nothing over these six patterns.
DISCUSSION_ENTRY_PATTERN = re.compile(
    r"<a\b(?=[^>]*\bdiscussion-link\b)"
    r"(?=[^>]*\bhref=(?P<q>['\"])(?P<href>.*?)(?P=q))"
    r"[^>]*>(?P<text>.*?)</a>",
    re.I | re.S,
)
PAGE_COUNT_PATTERN = re.compile(r"Page\s+\d+\s+of\s+(\d+)", re.I)
# ponytail: case sensitive on purpose. examtopics renders the total as "1019 Questions",
# while a discussion title reads "topic 1 question 135" -- a case-insensitive match here
# reads that as a total of 1. Verified capitalised on 8 exam pages across 6 providers.
QUESTION_COUNT_PATTERN = re.compile(r"\b([\d,]+)\s+Questions?\b")
CHOICE_PATTERN = re.compile(
    r"<li\b[^>]*\bclass=(?P<q>['\"])(?P<cls>[^'\"]*\bmulti-choice-item\b[^'\"]*)(?P=q)[^>]*>"
    r"(?P<body>.*?)</li>",
    re.I | re.S,
)
CHOICE_LETTER_PATTERN = re.compile(
    r"<span\b(?=[^>]*\bmulti-choice-letter\b)[^>]*>(.*?)</span>", re.I | re.S
)
VOTES_PATTERN = re.compile(
    r"<script\b[^>]*\btype=['\"]application/json['\"][^>]*>\s*(\[.*?\])\s*</script>",
    re.I | re.S,
)
CARD_TEXT_PATTERN = re.compile(
    r"<p\b(?=[^>]*\bcard-text\b)[^>]*>(?P<body>.*?)</p>", re.I | re.S
)
TITLE_PATTERN = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
PAGE_TITLE_PATTERN = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
IMAGE_PATTERN = re.compile(r"<img\b[^>]*\bsrc=['\"]([^'\"]+)['\"][^>]*>", re.I)
NOISE_PATTERN = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)

BLOCKED_MARKERS = (
    "checking your browser",
    "verify you are human",
    "please complete the security check",
    "cf-chl",
)
# Every real examtopics page carries the site nav; a Cloudflare interstitial does not.
# Verified present on all nine page shapes this project fetches.
CONTENT_SENTINEL = 'href="/exams/"'


def strip_html_text(value: str) -> str:
    """Tags out, entities decoded, all whitespace collapsed to single spaces."""
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def strip_question_text(value: str) -> str:
    """Like strip_html_text but keeps line breaks and image URLs.

    Many exam questions are diagrams, so dropping <img> would silently discard the
    whole question.
    """
    text = IMAGE_PATTERN.sub(lambda m: f"\n[image: {urljoin(BASE_URL, m.group(1))}]\n", value or "")
    text = re.sub(r"<br\s*/?>|</p\s*>|</div\s*>|</li\s*>", "\n", text, flags=re.I)
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"[^\S\n]+", " ", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def visible_text(html: str) -> str:
    """Page text with script/style bodies removed, so their contents cannot be matched."""
    return strip_html_text(NOISE_PATTERN.sub(" ", html or ""))


def is_blocked_html(html: str) -> bool:
    text = (html or "").lower()
    # ponytail: markers are only consulted once the site nav is absent. Matching them
    # against whole-page text discarded real questions -- "Access Denied" is ordinary
    # wording in AWS IAM questions, and it silently dropped 2 of 1019 on SAA-C03.
    if CONTENT_SENTINEL in text:
        return False
    return any(marker in text for marker in BLOCKED_MARKERS)


def raise_if_blocked(html: str):
    if is_blocked_html(html):
        raise RuntimeError("Blocked by anti-bot/captcha page")


def extract_discussion_entries(html: str) -> List[Tuple[str, str]]:
    """(link text, href) for every question on a provider discussion listing page."""
    return [
        (strip_html_text(match.group("text")), unescape(match.group("href")))
        for match in DISCUSSION_ENTRY_PATTERN.finditer(html)
    ]


def extract_exam_entries(html: str, provider: str) -> List[Tuple[str, str]]:
    """(exam slug, display name) for every exam linked on /exams/<provider>/."""
    pattern = re.compile(
        r"<a\b[^>]*\bhref=['\"]/exams/%s/([^/'\"]+)/['\"][^>]*>(.*?)</a>" % re.escape(provider),
        re.I | re.S,
    )
    entries: Dict[str, str] = {}
    for match in pattern.finditer(html):
        slug = match.group(1).lower()
        label = strip_html_text(match.group(2))
        # The anchor holds "CODE: Full Name" or "Name: Name (CODE)". The longer half is
        # always the more descriptive one.
        name = max((part.strip() for part in label.split(":")), key=len, default="")
        entries.setdefault(slug, name or slug)
    return sorted(entries.items())


def extract_providers(html: str) -> List[str]:
    """Provider slugs linked on /exams/."""
    return sorted(set(re.findall(r"href=['\"]/exams/([^/'\"]+)/['\"]", html, re.I)))


def parse_discussion_page_count(html: str) -> int:
    match = PAGE_COUNT_PATTERN.search(visible_text(html))
    if not match:
        raise RuntimeError("Could not find discussion page count")
    return int(match.group(1))


def parse_question_count(html: str) -> int:
    """Questions published for an exam, or 0 when the page does not say."""
    match = QUESTION_COUNT_PATTERN.search(visible_text(html))
    return int(match.group(1).replace(",", "")) if match else 0


def parse_discussion_title(html: str) -> str:
    """The "Exam X topic N question M discussion" heading of a discussion page.

    The <h1> on these pages is a promo banner, so <title> is the only place the exam
    and the question number appear together. The text it yields has the same shape as
    a listing link's, which is what lets matches_exam() and discussion_entry_url()
    handle a page found by id exactly as they handle one found on the listing.
    """
    match = PAGE_TITLE_PATTERN.search(html or "")
    text = strip_html_text(match.group(1)) if match else ""
    return re.sub(r"\s*[-|]\s*ExamTopics\s*$", "", text, flags=re.I)


def parse_question(html: str) -> Dict[str, object]:
    """Question, choices, suggested answer and community vote tally from a
    discussion page. A discussion page holds exactly one question."""
    title_match = TITLE_PATTERN.search(html)
    body_match = CARD_TEXT_PATTERN.search(html)

    choices: List[Tuple[str, str]] = []
    suggested_letters: List[str] = []
    for match in CHOICE_PATTERN.finditer(html):
        body = match.group("body")
        letter_match = CHOICE_LETTER_PATTERN.search(body)
        letter = strip_html_text(letter_match.group(1)).rstrip(".") if letter_match else ""
        choices.append((letter, strip_question_text(CHOICE_LETTER_PATTERN.sub(" ", body))))
        # ponytail: examtopics tags each suggested answer's <li> with "correct-hidden"
        # (it is what the paywalled "Show Suggested Answer" button reveals). "Choose
        # three" questions carry the class on three <li>, so collect them all rather
        # than keeping the last one.
        if "correct-hidden" in match.group("cls"):
            suggested_letters.append(letter)

    votes: List[Dict[str, object]] = []
    votes_match = VOTES_PATTERN.search(html)
    if votes_match:
        try:
            parsed = json.loads(unescape(votes_match.group(1)))
            votes = [vote for vote in parsed if isinstance(vote, dict)]
        except ValueError:
            votes = []
    community = next(
        (str(vote.get("voted_answers", "")) for vote in votes if vote.get("is_most_voted")), ""
    )
    # ponytail: is_most_voted is not always set, even on a tally with a single entry, so
    # fall back to the highest count instead of reporting no community answer.
    if not community and votes:
        top = max(votes, key=lambda vote: int(vote.get("vote_count", 0) or 0))
        community = str(top.get("voted_answers", ""))

    return {
        "title": strip_html_text(title_match.group(1)) if title_match else "",
        "text": strip_question_text(body_match.group("body")) if body_match else "",
        "choices": choices,
        "suggested": "".join(suggested_letters),
        "community": community,
        "votes": votes,
    }
