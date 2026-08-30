# Free Exam Dumps — ExamTopics Scraper for Any Certification Exam

**Download free ExamTopics practice questions and exam dumps from the terminal.** Type an
exam code like `SAA-C03`, `AZ-104` or `SY0-701` and get a plain text file with every public
question, all answer choices, the suggested answer, and the community vote split.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/swarnava-dutta/Free-Exam-Dumps.svg)](LICENSE)
[![Exams covered](https://img.shields.io/badge/exams-2%2C289-brightgreen.svg)](#supported-exams)
[![Providers](https://img.shields.io/badge/providers-187-brightgreen.svg)](#supported-exams)
[![Dependencies](https://img.shields.io/badge/dependencies-2-lightgrey.svg)](requirements.txt)

Covers **2,289 exams across 187 providers** — AWS, Microsoft Azure, Cisco, CompTIA, Google
Cloud, Fortinet, Salesforce, VMware, Oracle, ServiceNow, Palo Alto and the rest. Nothing is
hardcoded, so exams added to the site show up on their own.

Plain HTTP only. No browser, no headless runtime, no captcha solver, two dependencies.

**It does not bypass the paywall.** It reads discussion pages that are already public to
anyone with a browser. See [What this cannot do](#what-this-cannot-do) before you rely on it.

---

## Contents

- [What you get](#what-you-get)
- [Supported exams](#supported-exams)
- [Before you start](#before-you-start)
- [Getting started on Windows](#getting-started-on-windows)
- [Getting started on macOS or Linux](#getting-started-on-macos-or-linux)
- [Finding your exam](#finding-your-exam)
- [How long it takes](#how-long-it-takes)
- [What it keeps on disk](#what-it-keeps-on-disk)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [What this cannot do](#what-this-cannot-do)
- [Running the tests](#running-the-tests)
- [How it works, and why](#how-it-works-and-why)
- [Project layout](#project-layout)

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

## Supported exams

Every exam listed on ExamTopics, found by exam code or by name. A sample of what people
usually come here for — all verified present in the index:

| Exam code | Certification | Provider |
|---|---|---|
| `SAA-C03` | AWS Certified Solutions Architect – Associate | amazon |
| `DVA-C02` | AWS Certified Developer – Associate | amazon |
| `CLF-C02` | AWS Certified Cloud Practitioner | amazon |
| `SOA-C02` | AWS Certified SysOps Administrator – Associate | amazon |
| `AZ-900` | Microsoft Azure Fundamentals | microsoft |
| `AZ-104` | Microsoft Azure Administrator | microsoft |
| `AZ-204` | Developing Solutions for Microsoft Azure | microsoft |
| `AZ-305` | Designing Microsoft Azure Infrastructure Solutions | microsoft |
| `AI-900` | Microsoft Azure AI Fundamentals | microsoft |
| `DP-203` | Data Engineering on Microsoft Azure | microsoft |
| `PL-300` | Microsoft Power BI Data Analyst | microsoft |
| `SC-200` | Microsoft Security Operations Analyst | microsoft |
| `MS-900` | Microsoft 365 Fundamentals | microsoft |
| `MD-102` | Endpoint Administrator | microsoft |
| `GH-300` | GitHub Copilot | microsoft |
| `SY0-701` | CompTIA Security+ 2023 | comptia |
| `200-301` | Cisco Certified Network Associate (CCNA) | cisco |
| `CISSP` | Certified Information Systems Security Professional | isc |
| `PCNSE` | Palo Alto Networks Certified Network Security Engineer | palo-alto-networks |
| `associate-cloud-engineer` | Google Cloud Associate Cloud Engineer | google |
| `professional-cloud-architect` | Google Professional Cloud Architect | google |

Largest providers by exam count: microsoft (231), cisco (207), ibm (112), fortinet (102),
vmware (92), dell (86), hp (80), salesforce (71), juniper (70), sap (62), huawei (58).

That table is a sample, not the list. If ExamTopics has it, this finds it — type the code
and see. (ExamTopics publishes 189 provider pages; `elastic` and `fsmtb` list no exams at
all, which is why the provider count is 187.)

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
is reading the exam list for all 189 provider pages so it can recognise any code you type.

This takes about **30 seconds, once**. The finished list is saved to
`.examtopics_index.json` (about 165 KB) and reused, so every later run starts instantly.

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
Coverage:  1019 of 1019 published (100%)
```

The scan bar stops short of 100% on purpose. Once every published question has been found
there is nothing left to look for, so the remaining listing pages are skipped.

Run the same exam again and the completed files are reused immediately. To download a
fresh copy instead, run:

```text
.venv\Scripts\python.exe main.py --refresh
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
2289 exams indexed.

Exam:      HPE Campus Access Mobility Expert
Provider:  hp
```

That recheck happens at most once per run (~25s), so if you simply mistyped, the next
attempt is instant:

```text
Exam code or name: saa-c99
  'saa-c99' is not on the saved list. Checking examtopics.com...
2289 exams indexed.
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
| Already downloaded exam | instant |
| Small exam, e.g. `github-actions` (14 questions) | ~9s |
| Medium exam, e.g. `hpe7-a07` (18 questions, 96 pages) | ~17s |
| Large exam, `SAA-C03` (1019 questions, 604 pages) | **169s** |

Speed is limited by ExamTopics, not by the tool. Scanning runs at about 8 pages/second and
question fetching at about 11 questions/second. Using more parallel workers was measured
and does not help — see the notes at the bottom.

---

## What it keeps on disk

One hidden file, `.examtopics_index.json`, about **165 KB**. That is the list of 2,289 exams
and which provider each belongs to, saved so the ~190 requests behind it are not repeated
on every run. It has no expiry, and it is refreshed automatically when a search misses.

The two output files double as the cache. If their link and question counts match, the next
run returns them immediately. If only the links file exists after an interrupted run, the
slow provider scan is skipped. Use `--refresh` whenever you want current site data.

Earlier versions cached the pages too. It was removed: within a single run every page is
fetched exactly once, so the cache never sped up the run you were waiting on — it only
helped a *later* run, in exchange for **437 MB** of disk and three bugs (a stale question
count that cut scans short, unbounded growth, and a sweep that expired the wrong tier).
Deleting it made a full SAA-C03 run *faster*, 192s to 169s, because it no longer writes
250 MB of HTML while you wait.

Raw pages are still never cached. This avoids the old 437 MB cache while making repeat runs
instant and letting interrupted runs resume from the saved links.

Output files are overwritten by `--refresh`, so move or rename anything you want to keep.

---

## FAQ

**Is this free?** Yes. No account, no key, no paid tier, nothing to sign up for.

**Does it bypass the ExamTopics paywall?** No. Discussion pages are public; the tool reads
those. It does not log in, solve captchas, or touch contributor-only or paid content.

**Why do I get fewer questions than the `Published:` count?** Because only questions someone
has discussed have a public page. Popular exams come out complete; niche ones come out
sparse. Every run prints the exact coverage. See
[What this cannot do](#what-this-cannot-do).

**Which exams work?** All 2,289 on the site, across 187 providers. There is no supported-exam
list to maintain — the tool builds the index from ExamTopics itself, so new exams work the
day they are added.

**Can I get AZ-900, SAA-C03 or SY0-701 dumps with it?** Yes — those are just exam codes you
type at the prompt, same as any other. See [Supported exams](#supported-exams).

**Do I need Chrome, Selenium or Playwright?** No. It is plain HTTP with `requests`. Two
dependencies total.

**Does it work on macOS and Linux?** Yes. Only the two `.bat` helpers are Windows-specific;
run `main.py` directly instead.

**Are the answers correct?** `Suggested answer` is ExamTopics' answer and it is sometimes
wrong. That is exactly why the community vote is printed beside it. Use both, trust neither
blindly.

**How do I re-download an exam?** `--refresh`. Without it, finished output files are reused.

**Will it get me rate-limited or banned?** It makes ordinary GET requests at roughly the
speed a fast browser would, and backs off to a slow retry pass when the site pushes back.
Nothing here is stealthy, and nothing here hammers the site.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `'python' is not recognized` | Python is not installed, or you missed **Add python.exe to PATH**. Re-run the Python installer and tick that box. |
| `[ERROR] Could not create the virtual environment.` | Same cause as above. Install Python 3 from python.org, then re-run `install_dependencies.bat`. |
| `[WARN] .venv not found.` | You skipped Step 2. Double-click `install_dependencies.bat` first. |
| The window flashes open and closes instantly | Do not run the `.py` file directly. Use `run_scraper.bat`, which keeps the window open. |
| The scan bar stops at 76% but the files are written | Normal, and the run succeeded. Every published question was already found, so the rest of the provider's listing pages were skipped. |
| `No exam matches '...'` | The tool has already rechecked the site, so the exam genuinely is not there under that name. Type part of the exam name instead and pick from the list. |
| `is not on the saved list. Checking examtopics.com...` | Normal. The exam was added after you built the list, so it is being rebuilt. ~25s, once per run. |
| `No discussion links found for this exam.` | Nobody has posted discussions for that exam yet. There is nothing to download. |
| `[WARN] N pages failed after retries.` | A few requests were refused. The output is still written, just short by those pages. Wait a minute and run it again. |
| Fewer questions than the `Published:` count | Normal. See "What this cannot do" below. |
| It feels stuck on `Loading exam index` | It is fetching 189 pages. Give it 30 seconds. It only happens on the first run, or after deleting `.examtopics_index.json`. |

---

## What this cannot do

Be clear-eyed about this before you rely on it.

- **It does not bypass anything.** No login, no contributor access, no captcha solving, no
  paid tier. It reads pages that are already public to anyone with a browser.
- **You only get questions the community has discussed.** This is the big one, and it varies
  enormously by exam. Every fresh scrape ends with the number stated plainly:

  ```text
  Wrote github-actions dumps.txt  (14 questions)
  Coverage:  14 of 99 published (14%)
  ```

  Measured coverage:

  | Exam | Got | Published | Coverage | Question numbers |
  |---|---|---|---|---|
  | `saa-c03` | 1019 | 1019 | **100%** | 1–1019, no gaps |
  | `dva-c02` | 557 | 557 | **100%** | 1–557, no gaps |
  | `ai-900` | 246 | 246 | **100%** | 1–246, no gaps |
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

There is one test file with 11 checks. It needs no network and no test framework:

```text
.venv\Scripts\python.exe test_examtopics.py
```

```text
ok  test_block_detection_does_not_eat_real_pages
ok  test_exam_index_extraction_and_search
ok  test_exam_list_is_saved_reused_and_rebuilt
ok  test_exam_matching_is_anchored
ok  test_finished_outputs_are_reused
ok  test_multi_answer_question
ok  test_page_and_question_counts
ok  test_provider_normalization
ok  test_question_parsing
ok  test_question_parsing_tolerates_missing_parts
ok  test_url_rebuild_and_ordering

11 checks passed.
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
  found — SAA-C03 stops at page 480 of 604, AI-900 at page 1152 of 1519.
- **Exam matching is anchored** on `exam<slug>topic`. Without the anchor,
  `aws-certified-developer-associate` also matches every `...-dva-c02` question.
- **Link text is matched, not just the URL.** ExamTopics truncates long URLs before the
  `-topic` anchor, so SAA-C03 matches 0 of its entries by URL and all 1019 by link text.
- **24 parallel workers.** 16, 32, 64 and 96 were all measured: every one lands on ~6-8
  requests/second, so the limit is server-side and extra workers only add sockets.
- **Blocked-page detection requires the site nav to be missing.** Searching whole pages for
  phrases like "access denied" silently discarded real AWS IAM questions — 2 of 1019 on
  SAA-C03.
- **Raw pages are never cached.** Completed text outputs are reused instead. This gives
  instant repeat runs without the old 437 MB HTML cache or its stale-count bug.
- **Listing workers persist across chunks.** Their HTTP connections stay warm, and the
  provider's first listing page is reused instead of downloaded twice.
- **A fresh scrape fetches the published question count live**, because it decides when the
  scan stops early. Reading a stale low count stops the scan short: feeding the scanner an
  understated 200 on SAA-C03 returned 556 links instead of 1019.
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

## Contributing

Issues and pull requests are welcome. Run `test_examtopics.py` before opening one — it needs
no network, and each check guards a bug that actually happened.

If a provider's pages change shape and parsing breaks, an issue with the exam code and the
output you saw is enough to work from.

---

## License

See [LICENSE](LICENSE).

---

<sub>Keywords: examtopics scraper, examtopics downloader, free exam dumps, certification
practice questions, AWS SAA-C03 dumps, Azure AZ-104 / AZ-900 / AI-900 questions, CompTIA
SY0-701, Cisco CCNA 200-301, Google Cloud, CISSP, exam dump scraper, python cli.</sub>
