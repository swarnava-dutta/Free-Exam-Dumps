import threading
import time
from concurrent.futures import Executor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Iterator, Optional, Tuple

import requests

from .parsers import raise_if_blocked
from .settings import REQUEST_HEADERS, RETRIES, TIMEOUT, WORKERS


class HttpFetcher:
    """Retrying HTML GET that is safe to call from many threads.

    Pages are never cached. Within a run each page is fetched exactly once anyway, so a
    page cache only ever paid off across runs -- and it cost hundreds of MB of disk plus
    a stale-data bug class. The one thing worth keeping between runs is the exam list,
    which index.py stores as a single JSON file.
    """

    def __init__(self, timeout: int = TIMEOUT, retries: int = RETRIES):
        self.timeout = timeout
        self.retries = retries
        self._local = threading.local()

    def session(self) -> requests.Session:
        # ponytail: requests.Session is not documented as thread safe, so each thread
        # keeps its own. The default connection pool of 10 is ample because a thread
        # only ever has one request in flight.
        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers.update(REQUEST_HEADERS)
            self._local.session = session
        return session

    def fetch_html(self, url: str) -> str:
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session().get(url, timeout=self.timeout)
                response.raise_for_status()
                raise_if_blocked(response.text)
                return response.text
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(1.0 * (attempt + 1))

        raise RuntimeError(f"Failed to load {url}: {last_error}")


def parallel_results(
    function: Callable[[Any], Any],
    items: Iterable[Any],
    workers: int = WORKERS,
    executor: Optional[Executor] = None,
) -> Iterator[Tuple[Any, Any, Optional[BaseException]]]:
    """Yield (item, result, error) as each call finishes.

    The caller owns progress reporting and the failure policy, which keeps this the
    only place in the project that touches a thread pool.
    """
    owned = executor is None
    executor = executor or ThreadPoolExecutor(max_workers=max(1, workers))
    try:
        futures = {executor.submit(function, item): item for item in items}
        for future in as_completed(futures):
            try:
                yield futures[future], future.result(), None
            except Exception as exc:
                yield futures[future], None, exc
    finally:
        if owned:
            executor.shutdown()
