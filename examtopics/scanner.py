from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Tuple

from tqdm import tqdm

from .http_client import HttpFetcher, parallel_results
from .matching import (
    dedupe,
    discussion_entry_url,
    exam_match_key,
    extract_topic_question,
    matches_exam,
    provider_discussion_url,
)
from .parsers import extract_discussion_entries, parse_discussion_page_count, parse_question
from .settings import CHUNK_PAGES, RETRY_WORKERS, WORKERS

UNKNOWN_QUESTION = (10**9, 10**9)


def fetch_discussion_page(fetcher: HttpFetcher, provider: str) -> Tuple[int, str]:
    html = fetcher.fetch_html(provider_discussion_url(provider))
    return parse_discussion_page_count(html), html


def count_discussion_pages(fetcher: HttpFetcher, provider: str) -> int:
    return fetch_discussion_page(fetcher, provider)[0]


def scan_exam_links(
    fetcher: HttpFetcher,
    provider: str,
    exam_slug: str,
    total_pages: int,
    expected_questions: int = 0,
    first_page_html: str = "",
) -> List[str]:
    """Discussion links for one exam, found by scanning the provider's listing pages.

    There is no per-exam listing on the site and the free per-exam question view is
    paywalled past page 1, so scanning the provider listing is the only complete route.
    """
    key = exam_match_key(exam_slug)

    def page_links(page_number: int) -> List[str]:
        html = (
            first_page_html
            if page_number == 1 and first_page_html
            else fetcher.fetch_html(provider_discussion_url(provider, page_number))
        )
        return [
            discussion_entry_url(text, href)
            for text, href in extract_discussion_entries(html)
            if matches_exam(text, href, key)
        ]

    links: List[str] = []
    failed: List[int] = []
    with tqdm(total=total_pages, desc="Scanning pages", unit="pg") as bar:
        # Reuse threads across chunks so their HTTP sessions keep connections alive.
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for start in range(1, total_pages + 1, CHUNK_PAGES):
                chunk = range(start, min(start + CHUNK_PAGES, total_pages + 1))
                found, chunk_failed = _collect(page_links, chunk, WORKERS, bar, executor)
                failed.extend(chunk_failed)
                for page in found:
                    links.extend(page)

                links = dedupe(links)
                bar.set_postfix(found=len(links))
                # ponytail: stop as soon as every published question has been located.
                # Exact only when the exam has a discussion for each question, but when it
                # hits it saves scanning the rest of a 1500-page provider.
                if expected_questions and _distinct_questions(links) >= expected_questions:
                    break

    for page in _retry(page_links, failed, "pages"):
        links.extend(page)
    return dedupe(links)


def fetch_questions(fetcher: HttpFetcher, links: List[str]) -> List[Dict[str, object]]:
    """Question text, choices, suggested answer and vote tally for every link."""

    def load(link: str) -> Dict[str, object]:
        question = parse_question(fetcher.fetch_html(link))
        question["url"] = link
        question["sort_key"] = extract_topic_question(link)
        return question

    with tqdm(total=len(links), desc="Fetching questions", unit="q") as bar:
        questions, failed = _collect(load, links, WORKERS, bar)

    questions.extend(_retry(load, failed, "questions"))
    return sorted(questions, key=lambda item: item["sort_key"])


def _collect(function: Callable, items, workers: int, bar, executor=None) -> Tuple[List, List]:
    """Run function over items, advancing `bar`. Returns (results, failed items)."""
    results, failed = [], []
    for item, result, error in parallel_results(function, items, workers, executor):
        if error:
            failed.append(item)
        else:
            results.append(result)
        bar.update(1)
    return results, failed


def _retry(function: Callable, failed: List, label: str) -> List:
    """Second, slow pass over whatever failed. Recovers soft rate-limit blocks."""
    if not failed:
        return []

    print(f"  Retrying {len(failed)} {label} at low concurrency...")
    results = []
    still_failing = 0
    for item, result, error in parallel_results(function, failed, RETRY_WORKERS):
        if error:
            still_failing += 1
            print(f"  [WARN] {item} still failing: {error}")
        else:
            results.append(result)

    if still_failing:
        print(f"  [WARN] {still_failing} {label} could not be fetched. Output is incomplete.")
    return results


def _distinct_questions(links: List[str]) -> int:
    return len({extract_topic_question(link) for link in links} - {UNKNOWN_QUESTION})
