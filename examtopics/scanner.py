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
from .parsers import (
    extract_discussion_entries,
    parse_discussion_page_count,
    parse_discussion_title,
    parse_question,
)
from .settings import CHUNK_PAGES, ID_PAD, ID_ROUNDS, RETRY_WORKERS, WORKERS

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


def fill_missing_links(
    fetcher: HttpFetcher,
    provider: str,
    exam_slug: str,
    links: List[str],
    published: int,
) -> List[str]:
    """Recover questions the provider listing does not carry.

    A question only gets a listing entry once somebody posts about it, so an exam whose
    newer questions have drawn no comments comes back short however carefully the
    listing is scanned -- AI-103 gave up 81 of 135 that way. The discussion page exists
    regardless, and ids are handed out in contiguous per-exam batches, so the missing
    pages sit at ids beside the ones the listing did yield. Probe outward from those and
    keep whatever the page title says belongs to this exam.
    """
    key = exam_match_key(exam_slug)
    found = {extract_topic_question(link) for link in links} - {UNKNOWN_QUESTION}
    known = {_discussion_id(link) for link in links} - {0}
    if not known or not published or len(found) >= published:
        return links

    def view_url(page_id: int) -> str:
        # The slug after the id is decoration; examtopics keys the page off the id alone.
        return f"{provider_discussion_url(provider)}view/{page_id}-x/"

    def probe(page_id: int) -> str:
        return parse_discussion_title(fetcher.fetch_html(view_url(page_id)))

    print(f"Listing:   {len(found)} of {published}. Probing ids for the rest.")
    print()
    recovered: List[str] = []
    confirmed, probed = set(known), set(known)
    with tqdm(total=published - len(found), desc="Probing ids", unit="q") as bar:
        # Each round reaches further out from every id confirmed so far. That walks a
        # dense run of ids cheaply, and still crosses a stretch of another exam's ids
        # sitting inside this one's batch -- a fixed pad stops dead at the first such
        # stretch and leaves everything past it unfound.
        for reach in range(ID_PAD, ID_PAD * ID_ROUNDS + 1, ID_PAD):
            candidates = sorted(
                {
                    page_id
                    for seed in confirmed
                    for page_id in range(seed - reach, seed + reach + 1)
                }
                - probed
            )
            probed.update(candidates)
            for page_id, title, error in parallel_results(probe, candidates, WORKERS):
                if error or not matches_exam(title, "", key):
                    continue
                confirmed.add(page_id)
                link = discussion_entry_url(title, view_url(page_id))
                question = extract_topic_question(link)
                # UNKNOWN means the title carried no question number, so the link would
                # still be the "-x-" probe placeholder. Never write one of those out.
                if question == UNKNOWN_QUESTION:
                    continue
                recovered.append(link)
                # A number already held can still be a second, genuinely different page:
                # examtopics renumbers on republication and leaves both up. Keep it, but
                # count it once, or the published total is never reached.
                if question not in found:
                    found.add(question)
                    bar.update(1)
            # Deliberately no "stop on a round that found nothing": a gap wider than one
            # ID_PAD gives exactly that, and the next round is the one that clears it.
            if len(found) >= published:
                break

    print(f"Recovered: {len(recovered)} question{'' if len(recovered) == 1 else 's'} by id.")
    return dedupe(links + recovered)


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


def _discussion_id(link: str) -> int:
    """The numeric id from .../view/<id>-<slug>/, or 0 when the link has none."""
    tail = link.split("/view/", 1)[-1].split("-", 1)[0]
    return int(tail) if tail.isdigit() else 0
