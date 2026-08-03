"""Provider and exam index, built from examtopics' own /exams/ pages.

There is no single all-exams page on the site, so the index is one request for the
provider list plus one per provider. That is ~188 cached requests, roughly 25s once a
week, and it replaces asking the user to know the provider a code belongs to.
"""

from typing import List, Tuple

from .http_client import HttpFetcher, parallel_results
from .matching import normalize_slug
from .parsers import extract_exam_entries, extract_providers
from .settings import BASE_URL, INDEX_TTL

Exam = Tuple[str, str, str]  # (provider, exam slug, display name)


def load_exams(fetcher: HttpFetcher, on_progress=None, refresh: bool = False) -> List[Exam]:
    """`refresh` bypasses the cache, for when a brand-new exam is missing from it."""

    def read(url: str) -> str:
        if refresh:
            fetcher.cache.forget(url)
        return fetcher.fetch_html(url, INDEX_TTL)

    providers = extract_providers(read(f"{BASE_URL}/exams/"))

    def load(provider: str) -> List[Exam]:
        html = read(f"{BASE_URL}/exams/{provider}/")
        return [(provider, slug, name) for slug, name in extract_exam_entries(html, provider)]

    exams: List[Exam] = []
    for _, found, error in parallel_results(load, providers):
        if found:
            exams.extend(found)
        if on_progress:
            on_progress(error)
    return sorted(set(exams))


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
