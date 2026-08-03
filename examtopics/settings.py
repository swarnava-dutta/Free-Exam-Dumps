BASE_URL = "https://www.examtopics.com"

TIMEOUT = 30
RETRIES = 3

# ponytail: measured ceiling. 16/32/64/96 workers all landed on ~6-8 req/s against
# examtopics, so the cap is server side and extra workers only add sockets. Raise
# this only if a fresh measurement shows the cap moved.
WORKERS = 24

# How many pages to fetch before re-checking the early-stop condition.
CHUNK_PAGES = WORKERS * 4

# Second-pass concurrency. A captcha page is a rate-limit signal, so stragglers are
# re-fetched slowly instead of being reported as lost.
RETRY_WORKERS = 2

# The exam list, saved so the ~190 requests behind it are not repeated every run. No
# expiry: a list missing an exam shows up as a failed search, which rebuilds it.
INDEX_FILE = ".examtopics_index.json"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    # ponytail: Accept-Encoding is deliberately absent. requests advertises only the
    # codecs it can actually decode. Hardcoding "br" here makes examtopics reply with
    # brotli, which requests silently fails to decode when brotli is not installed --
    # you get a 200 with an unparseable body and zero results.
}
