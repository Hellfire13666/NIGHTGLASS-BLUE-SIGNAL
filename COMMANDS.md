# NIGHTGLASS // BLUE SIGNAL — Complete Command Directory

[← Back to the homepage](README.md)

Start the interactive terminal from the repository folder:

~~~bash
python3 -B COMMAND_CENTER.py
~~~

**00** exits · **25**, **HELP**, **?** print the complete interactive command directory. Use **08** for offline tests.

## Original Command Center (01–25)

| Number | Command | Description / source |
| --- | --- | --- |
| **01** | COMMENT FUSION | Fictional demonstration; offline parser, reply awareness, deduplication |
| **02** | IMPORT STATION | Permitted CSV/JSON/JSONL import; local reports |
| **03** | SEARCH LENS | Local text/name filtering of supplied exports |
| **04** | CROSS-REFERENCE | Compare two permitted exports; offline |
| **05** | REPORT VAULT | Open latest local HTML report |
| **06** | RECIPE DECK | Copyable recipes and source guidance |
| **07** | SYSTEM DOCTOR | Check local Python/module readiness |
| **08** | TEST SUITE | Run locally bundled unittest suite |
| **09** | LAYOUT | Current terminal width and display mode |
| **10** | COLORS | Toggle ANSI colors; terminal transparency untouched |
| **11** | SPOTLIGHT | Explanation of core modules 01–08 |
| **12** | THREAD EXPLORER | Navigate stored comments and search local reports |
| **13** | SOURCE BRIDGE | Inspect locally supplied file schema before import |
| **14** | THREAD FUSION | Review parent/reply relationships in local reports |
| **15** | RESEARCH DESK | Save/browse supplied Facebook link references |
| **16** | SOURCE GUARD | One opt-in public HTTP check; cooldown on repeat/restriction |
| **17** | INDEPENDENT SOURCE ENGINE | Offline/source research plus Page and Photo Post Fusion |
| **18** | POST HUNTER / LINK FUSION | Import records, discover public URL candidates, inspect sources |
| **19** | REPORT DECK | Print local JSON/CSV, list and open reports |
| **20** | EASY DEMO | Fictional post example without typing a filename |
| **21** | READ LATEST | Print latest Fusion JSON report |
| **22** | LIST REPORTS | List saved reports |
| **23** | EASY RESULTS | Simple reports/results navigation |
| **24** | ALL VERSIONS | Browse local report/archive views |
| **25** | HELP / ALL COMMANDS | Display complete numbered menu and descriptions |

**Source-status note:** The core engine uses offline files. Only specific user-invoked public checks request a URL; startup does not log into Facebook.

## Module 18: Post Hunter

~~~text
[1] Authorized Meta Page API — requires appropriate Page permission
[2] Import permitted CSV / JSON / JSONL — offline
[3] Original Public Post Fusion
[4] Smart Link Fusion — pasted/imported URLs, offline
[5] Public Post Discovery — one public HTML source
[6] Public Evidence Inspector — one public HTTPS Facebook URL
[7] LINK FUSION FAVORITES — Meta full / noisy / custom
[0] Return to Command Center
~~~

### Module 18 → 7: Link Fusion Favorites

~~~text
[1] META FULL — useful public links + HTTP checks
[2] META ALL LINKS / NOISY — includes resources
[3] CUSTOM FACEBOOK URL — full/noisy view
[0] Return to Post Hunter
~~~

Live results depend on accessible public HTML. All-links mode can list scripts/stylesheets and other assets. A discovered URL is **not** a verified post.

## Module 17: Independent Source Engine

Within the Source Engine, **17 → 5** opens offline Photo Post Fusion and **17 → 6** opens offline Page Research Fusion. These use locally supplied records; a URL-path match remains **unverified**.

## Copyable CLI recipes

**Command Center**

~~~bash
python3 -B COMMAND_CENTER.py
~~~

**Public link print and checks**

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
 'https://www.facebook.com/Meta' --check --focus
~~~

**All public references, including assets**

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
 'https://www.facebook.com/Meta' --check --all-links --full-urls
~~~

**Public link-path keyword hunt**

~~~bash
python3 NIGHTGLASS_LINK_FUSION_CORE.py \
 'https://www.facebook.com/Meta' --hunt 'posts,reels,photos'
~~~

**Public discovery (target is a cap, not a guaranteed count)**

~~~bash
python3 NIGHTGLASS_PUBLIC_DISCOVERY.py \
 --url 'https://www.facebook.com/Meta' --target 50
~~~

**Evidence metadata inspector**

~~~bash
python3 EVIDENCE_INSPECTOR.py \
 --url 'https://www.facebook.com/Meta'
~~~

**Offline link classification**

~~~bash
python3 NIGHTGLASS_SMART_LINK_FUSION.py \
 --file 'my-permitted-links.txt'
~~~

**Fictional post import**

~~~bash
python3 POST_HUNTER.py \
 --import-file examples/fictional_posts.csv
~~~

**Fictional comment import**

~~~bash
python3 -m nightglass import \
 examples/fictional_comments.csv \
 --limit 100 --out NightglassReports/example
~~~

**Offline source comparison**

~~~bash
python3 -m nightglass compare \
 examples/fictional_comments.csv \
 examples/fictional_comments.csv \
 --out NightglassReports/compare
~~~

**Self-test**

~~~bash
python3 -m unittest discover -s tests -v
~~~

See the [main README](README.md#-understanding-results) for result interpretation, privacy rules, and feature limitations. All examples use a public organizational page or fictional local data; replace local file names with your own permitted exports.
