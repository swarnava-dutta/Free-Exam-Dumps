# Free Exam Dumps Scraper

A terminal tool that downloads ExamTopics practice questions for any certification exam.

You type an exam code like `SAA-C03`. It finds the exam, collects every public discussion
page for it, and writes two plain text files: the links, and the questions themselves with
all answer choices, the suggested answer, and how the community voted.

Covers **2252 exams across 186 providers** on ExamTopics — AWS, Microsoft, Cisco, CompTIA,
Google, Fortinet, Salesforce, and the rest. Nothing is hardcoded, so new exams show up on
their own. (ExamTopics lists 188 providers, but `elastic` and `fsmtb` have no exams
published on the site at all.)

Plain HTTP only. No browser, no headless runtime, no captcha solver, two dependencies.

---

## What you get

A `<exam> dumps.txt` file full of entries like this:

```text
======================================================================
Topic 1 | Question 3
https://www.examtopics.com/discussions/github/view/321807-exam-github-actions-topic-1-question-3-discussion/

As a developer, which workflow steps should you perform to publish an image
to the GitHub Container Registry? (Choose three.)

A. Use the actions/setup-docker action
B. Authenticate to the GitHub Container Registry.
C. Build the container image.
D. Push the image to the GitHub Container Registry
E. Pull the image from the GitHub Container Registry.

Suggested answer: ABD
Community answer: BCD  [BCD 3 (100%)]
```

`Suggested answer` is ExamTopics' own answer. `Community answer` is what commenters voted
for, with the vote split. They disagree often, which is useful to see.

---

## Before you start

You need **Python 3.8 or newer**. That is all. (Developed and tested on Python 3.13.)

To check whether you already have it, open a terminal and run:

```text
python --version
```

If you see something like `Python 3.13.1`, you are ready — skip to Step 2.

If you see an error, or a version below 3.8, install Python first:

1. Go to <https://www.python.org/downloads/>
2. Download the latest version for your operating system.
3. **On Windows, tick "Add python.exe to PATH" on the first screen of the installer.**
   This is easy to miss and everything else depends on it.
4. Finish the installer, then close and reopen your terminal.

---

## Getting started on Windows

### Step 1 — Download the project

Either clone it with git:

```text
git clone https://github.com/swarnava-dutta/Free-Exam-Dumps.git
cd Free-Exam-Dumps
```

Or, if you do not have git: click the green **Code** button on the GitHub page, choose
**Download ZIP**, then right-click the downloaded file and **Extract All**. Open the
extracted folder.

### Step 2 — Run the installer, once

Double-click:

```text
install_dependencies.bat
```

A black window opens and does three things: creates a private Python environment in a
`.venv` folder, installs `requests` and `tqdm` into it, and stops. It leaves the rest of
your computer's Python untouched.

It takes about **25 seconds**. When you see this, it worked:

```text
============================================================
  Done. Next: double-click run_scraper.bat
============================================================
```

Press any key to close the window. You never need to run this again unless you move the
folder or delete `.venv`.

### Step 3 — Run the scraper

Double-click:

```text
run_scraper.bat
```

### Step 4 — Wait for the exam index, the first time only

On the very first run you will see a progress bar labelled `Loading exam index`. The tool
is reading the exam list for all 188 provider pages so it can recognise any code you type.

This takes about **30 seconds, once**. The finished list is saved to
`.examtopics_index.json` (about 160 KB) and reused, so every later run starts instantly.

### Step 5 — Type your exam code

```text
Exam code or name (example: SAA-C03, AZ-104, SY0-701): saa-c03
```

Press Enter. The tool confirms what it found before doing any work:

```text
Exam:      AWS Certified Solutions Architect - Associate SAA-C03
Provider:  amazon
Published: 1019 questions
Scanning:  604 discussion pages
```

Then it runs two passes, each with a progress bar and a live count:

```text
Scanning pages:  79%|#######9  | 480/604 [00:02<00:00, found=1019]

Wrote aws-certified-solutions-architect-associate-saa-c03 links.txt  (1019 links)

Fetching questions: 100%|##########| 1019/1019 [01:34<00:00, 10.77q/s]

Wrote aws-certified-solutions-architect-associate-saa-c03 dumps.txt  (1019 questions)
```

### Step 6 — Open your files

Both files land in the project folder, next to `main.py`:

| File | Contents |
|---|---|
| `<exam> links.txt` | every discussion URL, grouped by topic, in question order |
| `<exam> dumps.txt` | the questions, choices, suggested answer and vote split |

Open either one in Notepad, VS Code, or anything else. They are plain UTF-8 text.

The links file is written **before** the slower question pass starts, so if you get bored
and close the window you still keep the links.

---

## Getting started on macOS or Linux

The `.bat` files are Windows-only, but the tool itself is not. Run three commands:

```bash
git clone https://github.com/swarnava-dutta/Free-Exam-Dumps.git
cd Free-Exam-Dumps
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Then, to scrape:

```bash
.venv/bin/python main.py
```

Everything from Step 4 onward is identical.

---

## Finding your exam

You do **not** need to know which provider an exam belongs to. Type the code and the tool
works it out.

**An exact code goes straight through:**

```text
Exam code or name: az-104
Exam:      Microsoft Azure Administrator
Provider:  microsoft
```

**A partial name gives you a numbered list:**

```text
Exam code or name: solutions architect

   1. [microsoft] Agentic AI Business Solutions Architect
   2. [microsoft] Microsoft Azure Solutions Architect
   3. [ibm] IBM Cloud Solutions Architect v3
   4. [huawei] HCIP-Cloud Service Solutions Architect V3.5
   5. [amazon] AWS Certified Solutions Architect - Professional
   6. [amazon] AWS Certified Solutions Architect - Associate SAA-C02
   7. [amazon] AWS Certified Solutions Architect - Associate SAA-C03
   8. [amazon] AWS Certified Solutions Architect - Professional SAP-C02

Pick a number, or press Enter to search again:
```

Type a number and press Enter. Press Enter on its own to search again instead.

**A brand-new exam is fetched from the site automatically.** The saved exam list never
expires, so an exam added since you built it is not on it. Rather than telling you it does
not exist, the tool rechecks examtopics.com and searches again:

```text
Exam code or name: hpe7-a07
  'hpe7-a07' is not on the saved list. Checking examtopics.com...
2252 exams indexed.

Exam:      HPE Campus Access Mobility Expert
Provider:  hp
```

That recheck happens at most once per run (~25s), so if you simply mistyped, the next
attempt is instant:

```text
Exam code or name: saa-c99
  'saa-c99' is not on the saved list. Checking examtopics.com...
2252 exams indexed.
  No exam matches 'saa-c99'. Try an exam code such as SAA-C03.

Exam code or name: zzznotreal
  No exam matches 'zzznotreal'. Try an exam code such as SAA-C03.
```

Dashes, spaces and capitals do not matter. `SAA-C03`, `saa c03` and `saac03` all work.

---

## How long it takes

Measured on a normal home connection:

| | |
|---|---|
| Building the exam list, first run only | ~30s, then reused |
| Small exam, e.g. `github-actions` (14 questions) | ~9s |
| Medium exam, e.g. `hpe7-a07` (18 questions, 96 pages) | ~17s |
| Large exam, `SAA-C03` (1019 questions, 604 pages) | **169s** |

Speed is limited by ExamTopics, not by the tool. Scanning runs at about 8 pages/second and
question fetching at about 11 questions/second. Using more parallel workers was measured
and does not help — see the notes at the bottom.

---

## What it keeps on disk

One file, `.examtopics_index.json`, about **160 KB**. That is the list of 2252 exams and
which provider each belongs to, saved so the ~190 requests behind it are not repeated on
every run. It has no expiry, and it is refreshed automatically when a search misses.

**Nothing else is stored.** Every listing page, question page and question count is fetched
live on every run, so what you get is always current.

Earlier versions cached the pages too. It was removed: within a single run every page is
fetched exactly once, so the cache never sped up the run you were waiting on — it only
helped a *later* run, in exchange for **437 MB** of disk and three bugs (a stale question
count that cut scans short, unbounded growth, and a sweep that expired the wrong tier).
Deleting it made a full SAA-C03 run *faster*, 192s to 169s, because it no longer writes
250 MB of HTML while you wait.

What that trade gives up, honestly: re-running the same exam is no longer near-instant, a
second exam from the same provider no longer reuses the first one's listing pages, and an
interrupted run starts over rather than resuming.

Output files are overwritten each run, so move or rename anything you want to keep.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `'python' is not recognized` | Python is not installed, or you missed **Add python.exe to PATH**. Re-run the Python installer and tick that box. |
| `[ERROR] Could not create the virtual environment.` | Same cause as above. Install Python 3 from python.org, then re-run `install_dependencies.bat`. |
| `[WARN] .venv not found.` | You skipped Step 2. Double-click `install_dependencies.bat` first. |
| The window flashes open and closes instantly | Do not run the `.py` file directly. Use `run_scraper.bat`, which keeps the window open. |
| `No exam matches '...'` | The tool has already rechecked the site, so the exam genuinely is not there under that name. Type part of the exam name instead and pick from the list. |
| `is not on the saved list. Checking examtopics.com...` | Normal. The exam was added after you built the list, so it is being rebuilt. ~25s, once per run. |
| `No discussion links found for this exam.` | Nobody has posted discussions for that exam yet. There is nothing to download. |
| `[WARN] N pages failed after retries.` | A few requests were refused. The output is still written, just short by those pages. Wait a minute and run it again. |
| Fewer questions than the `Published:` count | Normal. See "What this cannot do" below. |
| It feels stuck on `Loading exam index` | It is fetching 188 pages. Give it 30 seconds. It only happens on the first run, or after deleting `.examtopics_index.json`. |

---

## What this cannot do

Be clear-eyed about this before you rely on it.

- **It does not bypass anything.** No login, no contributor access, no captcha solving, no
  paid tier. It reads pages that are already public to anyone with a browser.
- **You only get questions the community has discussed.** This is the big one, and it varies
  enormously by exam. Every run ends with the number stated plainly:

  ```text
  Wrote github-actions dumps.txt  (14 questions)
  Coverage:  14 of 99 published (14%)
  ```

  Measured coverage:

  | Exam | Got | Published | Coverage | Question numbers |
  |---|---|---|---|---|
  | `saa-c03` | 1019 | 1019 | **100%** | 1–1019, no gaps |
  | `dva-c02` | 557 | 557 | **100%** | 1–557, no gaps |
  | `gh-300` | 103 | 116 | 89% | 7 topics, 6 gaps |
  | `hpe7-a07` | 18 | 62 | 29% | 1–59, 41 gaps |
  | `github-actions` | 14 | 99 | 14% | 1–52, 38 gaps |

  Popular exams are complete. Niche ones are sparse, because a question nobody discussed
  has no public page to read. Nothing can fix that from outside the paywall.

- **Answers are not authoritative.** `Suggested answer` is ExamTopics' answer and it is
  sometimes wrong; that is exactly why the community vote is shown next to it. Use both.
- **Questions can go stale.** Exams get updated. Nothing here knows which questions are
  still current.

---

## Running the tests

There is one test file with 9 checks. It needs no network and no test framework:

```text
.venv\Scripts\python.exe test_examtopics.py
```

```text
ok  test_block_detection_does_not_eat_real_pages
ok  test_exam_index_extraction_and_search
ok  test_exam_matching_is_anchored
ok  test_multi_answer_question
ok  test_page_and_question_counts
ok  test_provider_normalization
ok  test_question_parsing
ok  test_question_parsing_tolerates_missing_parts
ok  test_url_rebuild_and_ordering

9 checks passed.
```

Run this after changing anything. Each check guards a bug that actually happened.

---

## How it works, and why

Every decision below came from measuring the live site, not from guessing.

- **Questions come from discussion pages, not exam pages.** `/exams/<provider>/<exam>/view/`
  is free for page 1 only; page 2 onward is a paywall. Discussion pages are free and carry
  the question, the choices, the suggested answer and the vote tally.
- **The suggested answer** is the choice ExamTopics tags with `correct-hidden` in its HTML,
  which is what its paywalled "Show Suggested Answer" button reveals. "Choose three"
  questions tag several, so all of them are collected.
- **There is no per-exam discussion listing**, so finding one exam's questions means scanning
  the provider's listing pages. The scan stops early once every published question has been
  found — SAA-C03 stops at page 480 of 604.
- **Exam matching is anchored** on `exam<slug>topic`. Without the anchor,
  `aws-certified-developer-associate` also matches every `...-dva-c02` question.
- **Link text is matched, not just the URL.** ExamTopics truncates long URLs before the
  `-topic` anchor, so SAA-C03 matches 0 of its entries by URL and all 1019 by link text.
- **24 parallel workers.** 16, 32, 64 and 96 were all measured: every one lands on ~6-8
  requests/second, so the limit is server-side and extra workers only add sockets.
- **Blocked-page detection requires the site nav to be missing.** Searching whole pages for
  phrases like "access denied" silently discarded real AWS IAM questions — 2 of 1019 on
  SAA-C03.
- **Pages are never cached.** Only the exam list is saved. Caching pages could not speed up
  the run you are waiting on, because each page is fetched once anyway — and it cost 437 MB
  plus a stale-count bug that cut scans short. Removing it made SAA-C03 go 192s to 169s.
- **The published question count is fetched live**, because it decides when the scan stops
  early. Reading a stale low count stops the scan short: feeding the scanner an understated
  200 on SAA-C03 returned 556 links instead of 1019.
- **Failures get a second slow pass.** Anything still missing after that is reported as a
  `[WARN]`, never silently dropped.

Repeatability was checked rather than assumed. Across `saa-c03`, `dva-c02`, `gh-300`,
`hpe7-a07` and `github-actions`:

- The early stop was compared against a full scan of every page on all five exams. Same
  links both ways, every time — it has never been observed to lose a question.
- Two independent scans of `saa-c03`, both downloading all 604 listing pages fresh, returned
  identical 1019-link sets.
- Two independent cold fetches of all 1154 questions across four exams produced identical
  results, with zero entries missing question text, choices, a suggested answer or a
  community answer, and no duplicate topic/question pairs.

One inherent caveat: the provider listing is ordered by last activity, so pages can shift
while a scan is in flight. No drift was observed in testing, and duplicates are removed
either way, but a very active provider could in principle move an entry across a page
boundary mid-scan. The coverage line is your check on that.

---

## Project layout

```text
main.py                     terminal app
install_dependencies.bat    one-time setup (Windows)
run_scraper.bat             launcher (Windows)
requirements.txt            requests, tqdm
test_examtopics.py          offline checks

examtopics/index.py         provider and exam index, exam code lookup
examtopics/scanner.py       listing scan and question fetch
examtopics/parsers.py       HTML extraction
examtopics/matching.py      slugs and exam matching
examtopics/http_client.py   retrying GET, thread pool
examtopics/output.py        the two output files
examtopics/settings.py      tunables
```

Want it faster or slower? Everything adjustable lives in `examtopics/settings.py`:
`WORKERS`, `TIMEOUT`, `RETRIES`, `CHUNK_PAGES` and `RETRY_WORKERS`.

---

## License

See [LICENSE](LICENSE).
