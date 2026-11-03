<div align="center">

![NIGHTGLASS // BLUE SIGNAL](assets/NIGHTGLASS-REPOSITORY-BANNER.jpg)

# NIGHTGLASS // BLUE SIGNAL

### GLITCHBYTE PHANTOM LABS

**Public-source Facebook reference research · Live terminal diagnostics · Local evidence review**

[**Quick start**](#quick-start) · [**Explore the modules**](#inside-nightglass) · [**Commands**](COMMANDS.md) · [**Privacy**](#privacy--accuracy)

</div>

---

## Quick start

NIGHTGLASS is a Python terminal toolkit. Download or clone the repository, open a terminal **inside its folder**, then run:

```bash
python3 -B COMMAND_CENTER.py
```

Or on Linux:

```bash
sh RUN.sh
```

The Command Center retains **01–25** menu options and its help footer. Type **25**, **HELP**, or **?** for guidance.

## Inside NIGHTGLASS

| Module | What it does |
| --- | --- |
| **Command Center** | Navigate the original 25-option terminal menu |
| **Link Fusion Favorites** | Inspect and print discoverable links and references from publicly accessible HTML |
| **Smart Link Fusion** | Classify supplied Facebook search, page, profile, and post-shaped URLs |
| **Public Post Discovery** | Find *references* exposed in accessible public HTML, without claiming a complete feed |
| **Evidence Inspector** | Review accessible metadata, redirects, and source-status indicators |
| **Post Hunter** | Work with authorized sources and locally imported CSV/JSON/JSONL records |
| **Page Research Fusion** | Compare saved page references against independently supplied local records |
| **Photo Post Fusion** | Organize supported imported photo/post records |
| **Source Guard** | Report source limits and avoid misleading results |

> **Source accuracy matters.** A public link, metadata tag, or post-shaped URL is *not* proof that the post's contents were retrieved or verified. Facebook may return a login page instead of requested content.

## See the artwork

The cover image above is stored in [`assets/NIGHTGLASS-REPOSITORY-BANNER.jpg`](assets/NIGHTGLASS-REPOSITORY-BANNER.jpg).

![NIGHTGLASS social preview](assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg)

The separate social preview is [`assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg`](assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg). GitHub's social-preview setting is configured separately under **Settings → General → Social preview**.

## Privacy & accuracy

- Use only public pages, permitted exports, or sources you are authorized to inspect.
- Results from public HTML may be incomplete. Clearly distinguish live observations from offline imports, demos, and unverified references.
- Do not publish private reports, local vault contents, browser sessions, cookies, access tokens, credentials, or backups.
- Examples are fictional; they are not real-person findings.
- This release does not provide authenticated access to private Facebook data.

## Repository guide

- [`COMMAND_CENTER.py`](COMMAND_CENTER.py) — main launcher
- [`POST_HUNTER.py`](POST_HUNTER.py) — post research and imported-record workflows
- [`NIGHTGLASS_LINK_FUSION_FAVORITES.py`](NIGHTGLASS_LINK_FUSION_FAVORITES.py) — public-link favorite recipes
- [`EVIDENCE_INSPECTOR.py`](EVIDENCE_INSPECTOR.py) — evidence reference diagnostics
- [`COMMANDS.md`](COMMANDS.md) — menu guidance
- [`tests/`](tests) — automated tests
- [`examples/`](examples) — fictional examples

---

<div align="center">

**NIGHTGLASS // BLUE SIGNAL**

*Bring the source. Check the signal. Keep the evidence honest.*

**GLITCHBYTE PHANTOM LABS**

</div>
