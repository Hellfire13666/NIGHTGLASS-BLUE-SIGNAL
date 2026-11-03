<div align="center">

![NIGHTGLASS // BLUE SIGNAL](assets/NIGHTGLASS-REPOSITORY-BANNER.jpg)

# NIGHTGLASS // BLUE SIGNAL
### GLITCHBYTE PHANTOM LABS

**Facebook public-source reference research • Neon terminal intelligence • Offline evidence fusion**

**01–25 Command Center** · **Post Hunter** · **Link Fusion** · **Evidence Inspector** · **Private local reports**

[Start here](#-quick-start) • [Tool modules](#-toolkit-overview) • [Real commands](#-copy-paste-recipes) • [Complete menu guide](COMMANDS.md) • [What results mean](#-understanding-results)

</div>

---

## ⚡ What is NIGHTGLASS?

NIGHTGLASS // BLUE SIGNAL is a Python research toolkit for **publicly available Facebook link references, HTML metadata, user-supplied exports, comment organization, and source checks**. It combines an interactive, colorful **25-option Command Center** with stand-alone utilities for link discovery, post-record review, report viewing, and evidence assessment.

The main goal is simple: **print useful information in the terminal, identify where it came from, and keep uncertain or unavailable information clearly labeled**.

It is **not** a Facebook account-access tool, a private friends/followers collector, a guarantee of complete post feeds, or a substitute for evidence verification. Some modules inspect one public web page when expressly selected; others work **entirely offline**.

### What makes this release different?

- **Live terminal-first output:** source links, detected references, HTTP responses, classifications, and totals when available.
- **25 original commands:** a single Command Center with a permanent help directory.
- **Seven Post Hunter paths:** permitted Page API, CSV/JSON/JSONL imports, original fusion, smart links, public discovery, evidence inspection, and Link Fusion Favorites.
- **Source Guard:** bounded public checks, restricted responses, and a cooldown instead of aggressive retries.
- **Private reports:** keep user-supplied and analyzed material on your own machine, **not in the GitHub repository**.
- **Demo without an account:** fictional sample files and offline unit tests.

> **Public-source boundary:** A reachable URL is not proof of accessible content. A metadata title does not establish authorship. A page that returns HTTP 200 may still be a generic login page. NIGHTGLASS marks references and imports accordingly.

## 🚀 Quick start

**Requirements:** Python 3 and a terminal. Standard-library-based core. Some optional public checks require network access.

Download or clone this repository, open a terminal **inside the extracted project folder**, then run:

~~~bash
python3 -B COMMAND_CENTER.py
~~~

**Linux shortcut**, from the same folder:

~~~bash
sh RUN.sh
~~~

**Explore without connecting to Facebook:**

~~~bash
python3 -m nightglass doctor
python3 -m nightglass examples
python3 -m nightglass demo --out NightglassReports/demo
~~~

The Command Center starts with its 25 numbered options. Choose **25**, **HELP**, or **?** for the directory, and **00** to exit. Public URL checks are opt-in.

## 🧩 Toolkit overview

| Component | Where to find it | What it does |
| --- | --- | --- |
| **Command Center** | \`COMMAND_CENTER.py\` | Central neon terminal, menus 01–25, recent local result indicators |
| **Comment Fusion** | \`nightglass/\` and menu 01 | Deduplicate, sort, browse, filter, and compare permitted comment exports |
| **Import Station & Search Lens** | Menu 02 / 03 | Read CSV, JSON, JSONL; inspect local records and search terms |
| **Cross-Reference & Thread Fusion** | Menu 04 / 14 | Compare two local sources and browse parent/reply relationships |
| **Source Bridge / Research Desk** | Menu 13 / 15 | Review file schemas and save manually supplied references |
| **Source Guard** | Menu 16 | One bounded public check with cooldown for restricted or repeated requests |
| **Post Hunter** | Menu 18 | Post record imports, public references, source diagnostics and favorites |
| **Public Post Discovery** | Post Hunter 5 | Look for post/reel/video-shaped URL candidates in *one* accessible HTML page |
| **Evidence Inspector** | Post Hunter 6 | Assess redirects, title/description metadata, login hints and access limits |
| **Link Fusion Favorites** | Menu 18 → 7 | Quick public Meta link check, full/noisy references, or custom Facebook URL |
| **Report Deck / Easy Results** | Menus 19 / 23 | Print saved local JSON/CSV, list reports, and navigate results |
| **Photo Post Fusion** | Menu 17 → 5 | Organize independently supplied offline photo/post records |
| **Page Research Fusion** | Menu 17 → 6 | Match saved page reference paths with local exports, marked unverified |
| **Tests** | Menu 08 or \`tests/\` | Run regression tests without using private Facebook accounts |

These are different **modes of access**. A local export remains imported data even if its rows contain Facebook URLs.

## 🔥 Copy-paste recipes

All examples below use public Facebook links, fictional samples, or permitted local files. Run from the repository folder.

### 1. Launch all 25 tools

~~~bash
python3 -B COMMAND_CENTER.py
~~~

Inside NIGHTGLASS: **18 → 7 → 1** for the Meta full public-link recipe, **18 → 7 → 2** for the all-links/noisy variant, or **18 → 7 → 3** for a custom public URL.

### 2. Print useful public links and check them

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
  'https://www.facebook.com/Meta' \
  --check --focus --max-checks 20
~~~

The checker prints source status, discovered URLs, grouped counts, and HTTP results. Output depends on what the page actually exposes.

### 3. Show every discoverable public link, including resources

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
  'https://www.facebook.com/Meta' \
  --check --all-links --full-urls
~~~

This is the **noisy** view. It may include JavaScript, stylesheets, images, redirects, and other resources rather than posts.

### 4. Hunt for terms in accessible metadata and link paths

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
  'https://www.facebook.com/Meta' \
  --hunt 'posts,photos,reels,videos'
~~~

Keyword matches identify **public HTML/link-path signals**, not verified article or post contents.

### 5. Public post/reel URL candidates, one page only

~~~bash
python3 NIGHTGLASS_PUBLIC_DISCOVERY.py \
  --url 'https://www.facebook.com/Meta' \
  --target 50
~~~

\`--target 50\` is a **maximum candidate display target**, not a promise to retrieve 50 posts. The result can be zero or much smaller. For entirely offline inspection of an HTML file you already have permission to use:

~~~bash
python3 NIGHTGLASS_PUBLIC_DISCOVERY.py \
  --html 'sample-public-page.html' --target 25
~~~

### 6. Inspect a public Facebook URL carefully

~~~bash
python3 EVIDENCE_INSPECTOR.py \
  --url 'https://www.facebook.com/Meta'
~~~

Prints URL type, HTTP status, redirect count, title, available Open Graph information, login hints, anchor count, and a **content-unverified** assessment. Add \`--save\` only when you want a private local metadata report.

### 7. Sort/classify user-supplied URLs, offline

~~~bash
python3 NIGHTGLASS_SMART_LINK_FUSION.py \
  --file 'my-permitted-links.txt' --target 50
~~~

The text file contains one or more Facebook URLs. The inspector distinguishes link shapes (search/profile/post/reel/etc.) without fetching them. A classification is **not** content verification.

### 8. Read a fictional post export directly in the terminal

~~~bash
python3 POST_HUNTER.py \
  --import-file examples/fictional_posts.csv
~~~

This prints each imported record's available date, ID, text and URL with a clear **LOCAL IMPORT** source label. Optional \`--save\` stores a report privately.

### 9. Test Comment Fusion with fictional records

~~~bash
python3 -m nightglass demo --out NightglassReports/demo
~~~

Or use the bundled fictional comment export:

~~~bash
python3 -m nightglass import \
  examples/fictional_comments.csv \
  --limit 100 \
  --out NightglassReports/comment-example
~~~

You can use \`--search\` on an independently supplied export to filter text and author fields.

### 10. Compare two permitted exports, offline

~~~bash
python3 -m nightglass compare \
  examples/fictional_comments.csv \
  examples/fictional_comments.csv \
  --out NightglassReports/compare-demo
~~~

Reports distinguish matched and conflicting records and records unique to either source.

### 11. Verify the installation

~~~bash
python3 -m unittest discover -s tests -v
~~~

Test results apply to **the exact version run**. They do not confirm current Facebook availability or completeness.

## 🖥️ Example terminal display

*Illustrative layout using fictional data; not a captured live Facebook result.*

~~~text
NIGHTGLASS // BLUE SIGNAL
[SOURCE] Public HTML only | Read-only | No login
[URL] https://www.facebook.com/Meta
[DISCOVERY] Processing publicly visible HTML references...
[TOTAL] discovered=<varies> unique=<varies> checked_ok=<varies>
[SOURCE STATUS] Public HTML links only;
                not authenticated posts, friends or followers.
~~~

*Illustrative offline post import (fictional examples):*

~~~text
NIGHTGLASS // POST HUNTER 100+ | LOCAL IMPORT
[001] 2026-01-01 | ID DEMO-001
 TEXT: FICTIONAL test post for research demo
 LINK: https://www.facebook.com/Meta/posts/10000001
[TOTAL] posts=2 | imported records, not live Facebook
~~~

Results are printed in the terminal. Save/report commands are separate, so users can choose when local files are created.

## 📚 All 25 Command Center commands

The complete numbered directory, explanatory notes and guided menu paths are in **[COMMANDS.md](COMMANDS.md)**. You can also open it directly inside the tool with **25** or **HELP**.

## 🧭 Understanding results

| Result | What it means | What it does **not** mean |
| --- | --- | --- |
| **HTTP 200** | A server returned a successful response | Requested post text was necessarily visible |
| **Public URL discovered** | A URL string appeared in accessible HTML | The URL has been independently authenticated |
| **POST / REEL classification** | The URL matches a recognizable shape | Its content, date or author is verified |
| **Open Graph metadata** | A page response exposed a title/description/type | The full underlying post was retrieved |
| **Imported post/comment** | A record came from a supplied file | NIGHTGLASS collected it live |
| **URL path match** | Saved page path resembles an imported record link | Authorship, association or public access is proven |
| **Source Guard restricted** | Access limitation or cooldown was recorded | Retry or bypass is authorized |

### Current boundaries

- No private friends/followers access, login bypass, browser-cookie extraction, or hidden profile collection.
- Public Facebook content can change, be unavailable, or show a login gate.
- Authorized Meta Page API access is **optional** and requires the appropriate permissions; not needed for offline recipes.
- Some older recipe shortcuts may refer to **separately installed historical components**. The self-contained examples above use files in this repository.

## 🔒 Privacy & responsible use

- Use public sources and exports you own or have permission to process.
- Keep private research, cookies, access tokens, account data, local sessions, and evidence reports **off GitHub**.
- Save personal results privately; inspect findings before publishing any screenshots or writeups.
- Use synthetic demo data when sharing usage examples.
- Avoid interpreting shared links or pending-post references as allegations or evidence of another person's conduct.

The code and demo files in this repository are distinct from any private local NIGHTGLASS vault.

## 🖼️ Artwork

**Repository cover**

![NIGHTGLASS repository banner](assets/NIGHTGLASS-REPOSITORY-BANNER.jpg)

**GitHub social preview**

![NIGHTGLASS social preview](assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg)

For link cards, upload the social image through **Repository Settings → General → Social preview**. Uploading it into \`assets/\` alone does not configure GitHub's social card.

## 📂 Project map

| Path | Purpose |
| --- | --- |
| [\`COMMAND_CENTER.py\`](COMMAND_CENTER.py) | Main terminal hub |
| [\`POST_HUNTER.py\`](POST_HUNTER.py) | Authorized/imported post workflows |
| [\`NIGHTGLASS_LINK_FUSION_CORE.py\`](NIGHTGLASS_LINK_FUSION_CORE.py) | Public HTML links and checking |
| [\`NIGHTGLASS_LINK_FUSION_FAVORITES.py\`](NIGHTGLASS_LINK_FUSION_FAVORITES.py) | Favorite recipes in Post Hunter |
| [\`NIGHTGLASS_PUBLIC_DISCOVERY.py\`](NIGHTGLASS_PUBLIC_DISCOVERY.py) | Candidate public URL discovery |
| [\`EVIDENCE_INSPECTOR.py\`](EVIDENCE_INSPECTOR.py) | Metadata / redirect assessment |
| [\`NIGHTGLASS_SMART_LINK_FUSION.py\`](NIGHTGLASS_SMART_LINK_FUSION.py) | Offline URL typing |
| [\`PAGE_RESEARCH_FUSION.py\`](PAGE_RESEARCH_FUSION.py) | Imported page-path comparisons |
| [\`nightglass/\`](nightglass/) | Offline comment engine and CLI |
| [\`examples/\`](examples/) | Fictional test inputs |
| [\`tests/\`](tests/) | Automated regression tests |
| [\`COMMANDS.md\`](COMMANDS.md) | Full menu explanations and quick recipes |

---

<div align="center">

### NIGHTGLASS // BLUE SIGNAL
**GlitchByte Phantom Labs**

*Bring the source. Check the signal. Let the evidence speak.*

</div>
