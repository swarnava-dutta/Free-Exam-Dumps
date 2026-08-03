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

    def _path_for(self, url: str) -> Optional[Path]:
        if self.cache_dir is None:
            return None
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.html"
