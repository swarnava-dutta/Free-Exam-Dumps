"""The provider and exam list, built from examtopics' own /exams/ pages.

There is no single all-exams page on the site, so building this costs one request for the
provider list plus one per provider -- about 190 requests and 30 seconds. That is too long
to pay before every prompt, so the finished list is saved as one JSON file and reused.

There is deliberately no expiry. A stale list only matters when it is missing an exam, and
that shows up immediately as a failed search, which rebuilds it. Everything else the tool
fetches -- listing pages, question pages, question counts -- is always live.
"""

import json
from pathlib import Path
from typing import List, Tuple

from .http_client import HttpFetcher, parallel_results
from .matching import normalize_slug
from .parsers import extract_exam_entries, extract_providers
from .settings import BASE_URL, INDEX_FILE

Exam = Tuple[str, str, str]  # (provider, exam slug, display name)


def load_exams(fetcher: HttpFetcher, on_progress=None, refresh: bool = False) -> List[Exam]:
    if not refresh:
        saved = _read_file()
        if saved:
            return saved

    providers = extract_providers(fetcher.fetch_html(f"{BASE_URL}/exams/"))

    def load(provider: str) -> List[Exam]:
        html = fetcher.fetch_html(f"{BASE_URL}/exams/{provider}/")
        return [(provider, slug, name) for slug, name in extract_exam_entries(html, provider)]

    exams: List[Exam] = []
    for _, found, error in parallel_results(load, providers):
        if found:
            exams.extend(found)
        if on_progress:
            on_progress(error)

    exams = sorted(set(exams))
    if exams:
        _write_file(exams)
    return exams


def find_exams(query: str, exams: List[Exam]) -> List[Exam]:
    """Exams matching a code or partial name. An exact slug hit wins outright."""
    needle = normalize_slug(query)
    if not needle:
        return []

    exact = [exam for exam in exams if normalize_slug(exam[1]) == needle]
    if exact:
        return exact

    hits = [
        exam
        for exam in exams
        if needle in normalize_slug(exam[1]) or needle in normalize_slug(exam[2])
    ]
    # Shortest slug first: a bare code like "az-104" ranks above "az-104-and-az-105".
    return sorted(hits, key=lambda exam: (len(exam[1]), exam[0], exam[1]))


def _read_file() -> List[Exam]:
    path = Path(INDEX_FILE)
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
        return [(row[0], row[1], row[2]) for row in rows if len(row) == 3]
    except (ValueError, OSError, IndexError, TypeError):
        # A truncated or hand-edited file just means rebuild from the site.
        return []


def _write_file(exams: List[Exam]):
    try:
        Path(INDEX_FILE).write_text(json.dumps([list(e) for e in exams]), encoding="utf-8")
    except OSError:
        # ponytail: losing the saved list costs 30s next run, nothing more. Do not fail
        # a scrape because a file could not be written.
        pass
