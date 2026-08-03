import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Iterator, Optional, Tuple

import requests

from .cache import HtmlCache
from .parsers import raise_if_blocked
from .settings import REQUEST_HEADERS, RETRIES, TIMEOUT, WORKERS


class HttpFetcher:
    """Cached, retrying HTML GET that is safe to call from many threads."""

    def __init__(self, cache: HtmlCache, timeout: int = TIMEOUT, retries: int = RETRIES):
        self.cache = cache
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

    def fetch_html(self, url: str, ttl_seconds: Optional[int] = None) -> str:
        # ponytail: disk cache with a TTL is the only caching option here. examtopics
        # serves no ETag and no Last-Modified (Cloudflare "DYNAMIC", Vary: Cookie), so
        # conditional GETs would always come back as a full 200.
        cached_html = self.cache.read(url, ttl_seconds)
        if cached_html is not None:
            return cached_html

        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session().get(url, timeout=self.timeout)
                response.raise_for_status()
                raise_if_blocked(response.text)
                self.cache.write(url, response.text)
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
) -> Iterator[Tuple[Any, Any, Optional[BaseException]]]:
    """Yield (item, result, error) as each call finishes.

    The caller owns progress reporting and the failure policy, which keeps this the
    only place in the project that touches a thread pool.
    """
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {executor.submit(function, item): item for item in items}
        for future in as_completed(futures):
            try:
                yield futures[future], future.result(), None
            except Exception as exc:
                yield futures[future], None, exc
