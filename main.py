from pathlib import Path

from tqdm import tqdm

from examtopics.cache import HtmlCache
from examtopics.http_client import HttpFetcher
from examtopics.index import find_exams, load_exams
from examtopics.matching import exam_url
from examtopics.output import write_links, write_questions
from examtopics.parsers import parse_question_count
from examtopics.scanner import count_discussion_pages, fetch_questions, scan_exam_links
from examtopics.settings import CACHE_DIR, INDEX_TTL, PAGE_TTL

MAX_CHOICES = 20


def main():
    print(f"\n{'=' * 60}\n  ExamTopics Scraper\n{'=' * 60}\n")

    fetcher = HttpFetcher(HtmlCache(Path(CACHE_DIR), PAGE_TTL))
    exams = load_exam_index(fetcher)
    provider, exam_slug, exam_name = choose_exam(exams)

    published = parse_question_count(fetcher.fetch_html(exam_url(provider, exam_slug), INDEX_TTL))
    total_pages = count_discussion_pages(fetcher, provider)

    print(f"\nExam:      {exam_name}")
    print(f"Provider:  {provider}")
    print(f"Published: {published or 'unknown'} questions")
    print(f"Scanning:  {total_pages} discussion page{'' if total_pages == 1 else 's'}\n")

    links = scan_exam_links(fetcher, provider, exam_slug, total_pages, published)
    if not links:
        print("\nNo discussion links found for this exam.")
        return

    links_path = f"{exam_slug} links.txt"
    write_links(links_path, links)
    print(f"\nWrote {links_path}  ({len(links)} links)\n")

    questions = fetch_questions(fetcher, links)
    dumps_path = f"{exam_slug} dumps.txt"
    write_questions(dumps_path, questions, exam_name, provider)
    print(f"\nWrote {dumps_path}  ({len(questions)} questions)")


def load_exam_index(fetcher: HttpFetcher):
    """Load the provider/exam index, showing a bar only while it is actually fetching."""
    bar = tqdm(desc="Loading exam index", unit="provider", leave=False)
    try:
        exams = load_exams(fetcher, on_progress=lambda error: bar.update(1))
    finally:
        bar.close()

    if not exams:
        raise SystemExit("Could not load the exam index. Check your connection.")
    print(f"{len(exams)} exams indexed.\n")
    return exams


def choose_exam(exams):
    """Resolve an exam code or name to exactly one (provider, slug, name)."""
    while True:
        query = input("Exam code or name (example: SAA-C03, AZ-104, SY0-701): ").strip()
        if not query:
            print("  [ERROR] Value is required.\n")
            continue

        hits = find_exams(query, exams)
        if not hits:
            print(f"  No exam matches '{query}'. Try an exam code such as SAA-C03.\n")
            continue
        if len(hits) == 1:
            return hits[0]

        print()
        for number, (provider, _, name) in enumerate(hits[:MAX_CHOICES], 1):
            print(f"  {number:2}. [{provider}] {name}")
        if len(hits) > MAX_CHOICES:
            print(f"  ... and {len(hits) - MAX_CHOICES} more. Narrow the search to see them.")

        answer = input("\nPick a number, or press Enter to search again: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= min(len(hits), MAX_CHOICES):
            return hits[int(answer) - 1]
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
