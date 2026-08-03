"""Offline checks for the parsing and matching logic. Run: python test_examtopics.py"""

import os
import tempfile
from pathlib import Path

import examtopics.index as index_module
from examtopics.index import find_exams, load_exams
from examtopics.matching import (
    discussion_entry_url,
    exam_match_key,
    extract_topic_question,
    matches_exam,
    normalize_provider,
    provider_discussion_url,
)
from examtopics.output import group_by_topic
from examtopics.parsers import (
    extract_discussion_entries,
    extract_exam_entries,
    is_blocked_html,
    parse_discussion_page_count,
    parse_question,
    parse_question_count,
)

LISTING_HTML = """
<div class="discussion-list-page-indicator">12074 Discussions Page <strong>1</strong> of <strong>604</strong></div>
<a class="btn discussion-link" href="/discussions/amazon/view/1-exam-aws-certified-developer-associate-dva-c02-topic-1/">
   Exam AWS Certified Developer Associate DVA-C02 topic 1 question 7 discussion</a>
<a href="/discussions/amazon/view/2-exam-aws-certified-developer-associate-topic-2/" class="discussion-link">
   Exam AWS Certified Developer Associate topic 2 question 9 discussion</a>
<a class="discussion-link" href="/discussions/amazon/view/3-exam-aws-certified-solutions-architect-associate-saa-c03/">
   Exam AWS Certified Solutions Architect - Associate SAA-C03 topic 1 question 40 discussion</a>
"""

MULTI_ANSWER_HTML = """
<h1>Exam GitHub Actions topic 1 question 4 discussion</h1>
<p class="card-text">Pick three.</p>
<script id="1" type="application/json">[{"voted_answers": "ADF", "vote_count": 2, "is_most_voted": false}]</script>
<ul>
  <li class="multi-choice-item correct-hidden"><span class="multi-choice-letter" data-choice-letter="A">A.</span> one</li>
  <li class="multi-choice-item"><span class="multi-choice-letter" data-choice-letter="B">B.</span> two</li>
  <li class="multi-choice-item correct-hidden"><span class="multi-choice-letter" data-choice-letter="C">C.</span> three</li>
  <li class="multi-choice-item correct-hidden"><span class="multi-choice-letter" data-choice-letter="D">D.</span> four</li>
</ul>
"""

QUESTION_HTML = """
<h1>Exam AWS Certified Cloud Practitioner CLF-C02 topic 1 question 135 discussion</h1>
<div class="question-body mt-3" data-id="898925">
  <p class="card-text">A company is assessing its plan.<br>Which benefit applies?
     <img src="/assets/media/x/1.png"></p>
  <div class="voted-answers-tally d-none">
    <script id="898925" type="application/json">[{"voted_answers": "C", "vote_count": 21, "is_most_voted": true},
      {"voted_answers": "D", "vote_count": 16, "is_most_voted": false}]</script>
  </div>
  <div class="question-choices-container"><ul>
    <li class="multi-choice-item"><span class="multi-choice-letter" data-choice-letter="A">A.</span> Trusted Advisor</li>
    <li class="multi-choice-item correct-hidden"><span class="multi-choice-letter" data-choice-letter="C">C.</span> A designated TAM</li>
  </ul></div>
</div>
<p>452 Questions</p>
"""

EXAMS_HTML = """
<a href="/exams/amazon/ans-c00/">ANS-C00: AWS Certified Advanced Networking - Specialty</a>
<a href="/exams/amazon/aws-certified-ai-practitioner-aif-c01/" class="popular-exam-link">
   <strong>AWS Certified AI Practitioner AIF-C01</strong>: AWS Certified AI Practitioner AIF-C01</a>
<a href="/exams/microsoft/az-104/">AZ-104</a>
"""


def test_provider_normalization():
    # The bug this guards: lower() alone left spaces in and produced a 404 URL.
    assert normalize_provider("Palo Alto Networks") == "palo-alto-networks"
    assert normalize_provider("C++ Institute") == "c-institute"
    assert normalize_provider("  Amazon ") == "amazon"
    assert normalize_provider("https://www.examtopics.com/discussions/hp/5/") == "hp"
    assert normalize_provider("/exams/microsoft/az-104/") == "microsoft"
    assert normalize_provider("") == ""
    assert " " not in provider_discussion_url("Palo Alto Networks")
    assert provider_discussion_url("amazon", 1).endswith("/discussions/amazon/")
    assert provider_discussion_url("amazon", 7).endswith("/discussions/amazon/7/")


def test_exam_matching_is_anchored():
    entries = extract_discussion_entries(LISTING_HTML)
    assert len(entries) == 3, entries

    def matched(exam_slug):
        key = exam_match_key(exam_slug)
        return [text for text, href in entries if matches_exam(text, href, key)]

    # A shorter slug must not swallow the longer one that contains it.
    assert len(matched("aws-certified-developer-associate")) == 1
    assert len(matched("aws-certified-developer-associate-dva-c02")) == 1
    assert matched("aws-certified-developer-associate") != matched(
        "aws-certified-developer-associate-dva-c02"
    )
    # Long slugs get truncated out of the href, so the text path must carry the match.
    saa = matched("aws-certified-solutions-architect-associate-saa-c03")
    assert len(saa) == 1 and "SAA-C03" in saa[0]
    assert matched("citrix-cca-v") == []


def test_page_and_question_counts():
    assert parse_discussion_page_count(LISTING_HTML) == 604
    assert parse_question_count(QUESTION_HTML) == 452
    assert parse_question_count("<p>no counts here</p>") == 0
    assert parse_question_count("<p>1,019 Questions</p>") == 1019
    # A count inside a script body must not be picked up.
    assert parse_question_count('<script>var s = "999 Questions";</script><p>7 Questions</p>') == 7
    # A discussion title says "topic 1 question 135"; that lowercase form is not a total.
    assert parse_question_count("<h1>Exam X topic 1 question 135 discussion</h1>") == 0


def test_question_parsing():
    question = parse_question(QUESTION_HTML)
    assert question["suggested"] == "C", question["suggested"]
    assert question["community"] == "C"
    assert [letter for letter, _ in question["choices"]] == ["A", "C"]
    assert question["choices"][1][1] == "A designated TAM"
    assert "A company is assessing its plan." in question["text"]
    # <br> becomes a newline, and the image survives as an absolute URL.
    assert "\nWhich benefit applies?" in question["text"]
    assert "[image: https://www.examtopics.com/assets/media/x/1.png]" in question["text"]
    assert sum(vote["vote_count"] for vote in question["votes"]) == 37


def test_exam_list_is_saved_reused_and_rebuilt():
    """The saved list must be reused without hitting the network, and rebuilt on refresh."""

    class FakeFetcher:
        """Serves two providers, and counts requests so reuse is provable."""

        def __init__(self):
            self.requests = 0

        def fetch_html(self, url):
            self.requests += 1
            if url.endswith("/exams/"):
                return '<a href="/exams/amazon/">A</a><a href="/exams/github/">G</a>'
            provider = url.rstrip("/").rsplit("/", 1)[-1]
            return f'<a href="/exams/{provider}/{provider}-x/">{provider.upper()}-X: Full Name</a>'

    with tempfile.TemporaryDirectory() as directory:
        original = index_module.INDEX_FILE
        index_module.INDEX_FILE = os.path.join(directory, "index.json")
        try:
            fetcher = FakeFetcher()
            first = load_exams(fetcher)
            assert first == [
                ("amazon", "amazon-x", "Full Name"),
                ("github", "github-x", "Full Name"),
            ], first
            assert fetcher.requests == 3, "one /exams/ plus one per provider"
            assert Path(index_module.INDEX_FILE).exists(), "list was not saved"

            # A second load must come off disk, touching the network zero times.
            reused = load_exams(fetcher)
            assert reused == first
            assert fetcher.requests == 3, "saved list was not reused"

            # refresh=True must go back to the site even though the file is present.
            assert load_exams(fetcher, refresh=True) == first
            assert fetcher.requests == 6, "refresh did not re-fetch"

            # A corrupt file must be rebuilt rather than crash.
            Path(index_module.INDEX_FILE).write_text("{not json", encoding="utf-8")
            assert load_exams(fetcher) == first
            assert fetcher.requests == 9, "corrupt file was not rebuilt"
        finally:
            index_module.INDEX_FILE = original


def test_block_detection_does_not_eat_real_pages():
    # A real question that happens to discuss Access Denied errors is not a block.
    real = '<a href="/exams/">All</a><p>Troubleshoot Access Denied errors in IAM.</p>'
    assert is_blocked_html(real) is False
    # A genuine interstitial has no site nav.
    assert is_blocked_html("<h1>Checking your browser before accessing</h1>") is True
    assert is_blocked_html('<script src="/cdn-cgi/challenge-platform/cf-chl/x.js">') is True
    assert is_blocked_html("") is False


def test_multi_answer_question():
    question = parse_question(MULTI_ANSWER_HTML)
    # "Choose three" tags three <li>; keeping only the last one reported a single letter.
    assert question["suggested"] == "ACD", question["suggested"]
    # is_most_voted is false on every entry here, so the highest count must still win.
    assert question["community"] == "ADF", question["community"]


def test_question_parsing_tolerates_missing_parts():
    question = parse_question("<h1>Bare page</h1>")
    assert question == {
        "title": "Bare page",
        "text": "",
        "choices": [],
        "suggested": "",
        "community": "",
        "votes": [],
    }


def test_url_rebuild_and_ordering():
    text = "Exam AWS Certified Developer Associate DVA-C02 topic 3 question 12 discussion"
    href = "/discussions/amazon/view/99-exam-aws-certified-developer-associate-dva/"
    rebuilt = discussion_entry_url(text, href)
    assert rebuilt.startswith("https://www.examtopics.com/discussions/amazon/view/99-exam-")
    assert rebuilt.endswith("topic-3-question-12-discussion/")
    assert extract_topic_question(rebuilt) == (3, 12)

    # A link with no topic/question sorts last rather than crashing.
    plain = "https://www.examtopics.com/discussions/amazon/view/5-something/"
    assert discussion_entry_url("no numbers here", "/discussions/amazon/view/5-something/") == plain
    assert extract_topic_question(plain) == (10**9, 10**9)

    grouped = group_by_topic([rebuilt, plain])
    assert list(grouped) == [3, 10**9]


def test_exam_index_extraction_and_search():
    entries = extract_exam_entries(EXAMS_HTML, "amazon")
    assert dict(entries) == {
        "ans-c00": "AWS Certified Advanced Networking - Specialty",
        "aws-certified-ai-practitioner-aif-c01": "AWS Certified AI Practitioner AIF-C01",
    }, entries

    exams = [
        ("amazon", "aws-certified-solutions-architect-associate-saa-c03", "SAA-C03 name"),
        ("amazon", "aws-certified-solutions-architect-associate-saa-c02", "SAA-C02 name"),
        ("microsoft", "az-104", "AZ-104 name"),
    ]
    assert find_exams("saa-c03", exams) == [exams[0]]
    assert find_exams("SAA C03", exams) == [exams[0]]
    # An exact slug hit wins outright instead of returning every partial match.
    assert find_exams("az-104", exams) == [exams[2]]
    assert len(find_exams("solutions-architect", exams)) == 2
    assert find_exams("nope", exams) == []
    assert find_exams("", exams) == []


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} checks passed.")
