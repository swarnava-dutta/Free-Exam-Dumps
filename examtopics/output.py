from typing import Dict, List

from .matching import extract_topic_question

SEPARATOR = "=" * 70
UNKNOWN_TOPIC = 10**9


def read_links(path: str) -> List[str]:
    """Read URLs previously written by write_links()."""
    try:
        with open(path, encoding="utf-8") as file:
            return [line[3:].strip() for line in file if line.startswith(" - https://")]
    except OSError:
        return []


def cached_question_count(links_path: str, dumps_path: str) -> int:
    """Question count when both existing output files form a complete result."""
    links = read_links(links_path)
    if not links:
        return 0
    try:
        with open(dumps_path, encoding="utf-8") as file:
            lines = [line.strip() for line in file]
        declared = int(
            next(line.split(": ", 1)[1] for line in lines[:3] if line.startswith("Questions: "))
        )
    except (OSError, StopIteration, ValueError):
        return 0
    sections = lines.count(SEPARATOR)
    complete = lines and lines[-1].startswith("Community answer:")
    return len(links) if declared == sections == len(links) and complete else 0


def group_by_topic(links: List[str]) -> Dict[int, List[str]]:
    """Links bucketed by topic, each bucket in question order."""
    grouped: Dict[int, List[str]] = {}
    for link in sorted(links, key=lambda item: (extract_topic_question(item), item)):
        grouped.setdefault(extract_topic_question(link)[0], []).append(link)
    return grouped


def write_links(path: str, links: List[str]):
    """Discussion links grouped by topic, in topic/question order."""
    with open(path, "w", encoding="utf-8") as file:
        for topic, topic_links in group_by_topic(links).items():
            label = "Unknown Topic" if topic == UNKNOWN_TOPIC else f"Topic {topic}"
            file.write(f"{label}:\n")
            for link in topic_links:
                file.write(f" - {link}\n")
            file.write("\n")


def write_questions(path: str, questions: List[Dict[str, object]], exam_name: str, provider: str):
    """Readable dump: question, choices, suggested answer, community vote split."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"{exam_name}\n")
        file.write(f"Provider: {provider}\n")
        file.write(f"Questions: {len(questions)}\n")

        for question in questions:
            topic, number = question["sort_key"]
            heading = (
                question["title"]
                if topic == UNKNOWN_TOPIC
                else f"Topic {topic} | Question {number}"
            )
            file.write(f"\n{SEPARATOR}\n{heading}\n{question['url']}\n\n")
            file.write(f"{question['text']}\n\n")

            for letter, text in question["choices"]:
                file.write(f"{letter}. {text}\n")

            file.write(f"\nSuggested answer: {question['suggested'] or 'not shown'}\n")
            file.write(f"Community answer: {_community_line(question)}\n")


def _community_line(question: Dict[str, object]) -> str:
    votes = question.get("votes") or []
    total = sum(int(vote.get("vote_count", 0) or 0) for vote in votes)
    if not total:
        return "no votes"

    parts = []
    for vote in sorted(votes, key=lambda item: -int(item.get("vote_count", 0) or 0)):
        count = int(vote.get("vote_count", 0) or 0)
        parts.append(f"{vote.get('voted_answers', '?')} {count} ({count * 100 // total}%)")
    return f"{question['community'] or '?'}  [{', '.join(parts)}]"
