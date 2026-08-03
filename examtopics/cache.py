import hashlib
import time
from pathlib import Path
from typing import Optional


class HtmlCache:
    """URL -> HTML on disk, keyed by URL digest, expired by mtime age."""

    def __init__(self, cache_dir: Optional[Path], ttl_seconds: int):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds

    def read(self, url: str, ttl_seconds: Optional[int] = None) -> Optional[str]:
        path = self._path_for(url)
        if path is None or not path.exists():
            return None
        ttl = self.ttl_seconds if ttl_seconds is None else ttl_seconds
        if ttl > 0 and time.time() - path.stat().st_mtime > ttl:
            return None
        return path.read_text(encoding="utf-8")

    def write(self, url: str, html: str):
        path = self._path_for(url)
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    def forget(self, url: str):
        """Drop one entry so the next fetch goes to the network."""
        path = self._path_for(url)
        if path is not None:
            path.unlink(missing_ok=True)

    def purge_older_than(self, max_age_seconds: int) -> int:
        """Delete entries past `max_age_seconds` and return how many went.

        Read alone never removes anything, so without this the cache grows without
        bound: ~600MB after seven exams, 332MB of it one provider's listing pages.
        `max_age_seconds` must be the longest TTL in use, since entries are written with
        different lifetimes and nothing on disk records which.
        """
        if self.cache_dir is None or max_age_seconds <= 0:
            return 0

        cutoff = time.time() - max_age_seconds
        removed = 0
        for path in self.cache_dir.glob("*.html"):
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink()
                    removed += 1
            except OSError:
                # ponytail: a file vanishing mid-sweep is fine, skip it.
                pass
        return removed

    def _path_for(self, url: str) -> Optional[Path]:
        if self.cache_dir is None:
            return None
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.html"
