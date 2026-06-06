#!/usr/bin/env python3
"""
check_refs.py — orchestrate bibsleuth verification + abstract fetch, emit a
markdown source-of-truth file that Grumpy uses to ground reference reviews.

Usage:
    python3 tools/refs-check/check_refs.py PAPER.bib [--output OUT.md]

Behaviour:
- Runs `bibsleuth check PAPER.bib --no-llm --format both -o <tmp>` (deterministic,
  no LLM cost; pure existence + metadata triangulation across 6 providers).
- For each reference that has a candidate DOI, fetches the abstract:
    1) Semantic Scholar (cleanest output)
    2) OpenAlex (inverted-index, de-inverted here)
    3) Crossref (JATS XML, stripped here)
- Emits / updates a markdown file with one section per reference:
    citation · bibsleuth verdict · score · DOI · abstract · placeholders for
    Grumpy's manual assessment (cited-at, claim, supported-or-not).

Idempotent: if the output file already exists, ref entries already present
are preserved (Grumpy's manual fields are not overwritten); only new
references in the .bib get appended.

Marc's standing rule (2026-05-28): the output file is the source of truth.
Subsequent Grumpy reviews of the same document read this file rather than
re-running bibsleuth. See skills/grumpy-check-refs.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

USER_AGENT = "ludo-writting-workshop/refs-check (mailto:marc.alier@upc.edu)"
# A separate, browser-like UA for URL-liveness checks (publishers/blog hosts
# often 403 the polite identifier above; a Safari UA passes most filters).
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
TIMEOUT = 15
URL_TIMEOUT = 10


def http_get_json(url: str) -> dict | None:
    """Fetch JSON from a URL with our standard User-Agent. Returns None on failure."""
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_abstract(doi: str) -> tuple[str | None, str | None]:
    """Try Semantic Scholar → OpenAlex → Crossref. Returns (abstract_text, provider)."""
    if not doi:
        return None, None

    # 1) Semantic Scholar — cleanest abstract field
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='/')}?fields=abstract"
    data = http_get_json(url)
    if data and data.get("abstract"):
        return data["abstract"], "semantic_scholar"

    # 2) OpenAlex — inverted index needs un-inverting
    url = f"https://api.openalex.org/works/doi:{quote(doi, safe='/')}"
    data = http_get_json(url)
    if data and data.get("abstract_inverted_index"):
        inv = data["abstract_inverted_index"]
        positions: dict[int, str] = {}
        for word, idxs in inv.items():
            for i in idxs:
                positions[i] = word
        if positions:
            ordered = [positions[i] for i in sorted(positions)]
            return " ".join(ordered), "openalex"

    # 3) Crossref — JATS XML in the `abstract` field
    url = f"https://api.crossref.org/works/{quote(doi, safe='/')}"
    data = http_get_json(url)
    if data and data.get("message", {}).get("abstract"):
        raw = data["message"]["abstract"]
        # Strip JATS / HTML tags
        text = re.sub(r"<[^>]+>", "", raw).strip()
        if text:
            return text, "crossref"

    return None, None


def check_url_liveness(url: str, cited_title: str | None = None) -> dict:
    """
    Check whether a URL is reachable and (if possible) whether the page title
    is consistent with the cited title.

    Returns a dict:
      {
        "status": "alive" | "dead" | "blocked" | "unreachable" | "timeout",
        "http_code": int | None,
        "final_url": str | None,        # after following redirects
        "page_title": str | None,
        "title_match": "match" | "partial" | "mismatch" | None,
        "notes": str,
      }

    "blocked" means a 401/403/429 — page exists but our request was refused.
    Distinguishable from "dead" (404/410); blocked URLs are NOT proof of
    fabrication and Grumpy should escalate them rather than flag them.
    """
    if not url:
        return {"status": "no-url", "http_code": None, "final_url": None,
                "page_title": None, "title_match": None,
                "notes": "no URL provided in bib entry"}

    req = Request(url, headers={
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en,ca;q=0.9,es;q=0.8",
    })

    try:
        with urlopen(req, timeout=URL_TIMEOUT) as resp:
            http_code = resp.status
            final_url = resp.geturl()
            # Read up to ~64 KB — enough for <title> and <h1> in any reasonable page
            body = resp.read(65536)
            charset = resp.headers.get_content_charset() or "utf-8"
            try:
                html = body.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                html = body.decode("utf-8", errors="replace")
    except HTTPError as e:
        http_code = e.code
        if http_code in (401, 403, 429):
            return {"status": "blocked", "http_code": http_code, "final_url": None,
                    "page_title": None, "title_match": None,
                    "notes": f"HTTP {http_code} — request refused (paywall, bot-blocker, or rate limit); URL existence indeterminate"}
        if http_code in (404, 410):
            return {"status": "dead", "http_code": http_code, "final_url": None,
                    "page_title": None, "title_match": None,
                    "notes": f"HTTP {http_code} — page not found (possible link rot, possible fabrication)"}
        return {"status": "unreachable", "http_code": http_code, "final_url": None,
                "page_title": None, "title_match": None,
                "notes": f"HTTP {http_code}"}
    except (URLError, TimeoutError) as e:
        msg = str(e)
        if "timed out" in msg.lower() or "timeout" in msg.lower():
            return {"status": "timeout", "http_code": None, "final_url": None,
                    "page_title": None, "title_match": None,
                    "notes": f"timed out after {URL_TIMEOUT}s"}
        return {"status": "unreachable", "http_code": None, "final_url": None,
                "page_title": None, "title_match": None,
                "notes": f"URL error: {msg[:120]}"}
    except Exception as e:
        # Catch socket.timeout (Python 3.9), ssl errors, and anything else
        # urllib might surface that isn't caught above. Better to mark a single
        # URL as unreachable than to crash the whole 44-ref batch.
        return {"status": "unreachable", "http_code": None, "final_url": None,
                "page_title": None, "title_match": None,
                "notes": f"fetch exception: {type(e).__name__}: {str(e)[:100]}"}

    # Extract title — prefer og:title, fall back to <title>, then first <h1>
    page_title = None
    og = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og:
        page_title = og.group(1).strip()
    if not page_title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            page_title = re.sub(r"\s+", " ", m.group(1)).strip()
    if not page_title:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if m:
            # Strip any nested tags
            page_title = re.sub(r"<[^>]+>", "", m.group(1))
            page_title = re.sub(r"\s+", " ", page_title).strip()

    # Title match — token-overlap heuristic on title, with body-search fallback
    title_match = None
    if cited_title and page_title:
        title_match = compare_titles(cited_title, page_title)
        # Body-search fallback — many pages re-title content (publishers wrap
        # original titles in their own framing). If title comparison says
        # mismatch, look for the cited title's substantive tokens in the body.
        if title_match in ("mismatch", "partial"):
            body_match = body_contains_cited_title(html, cited_title)
            if body_match == "match":
                title_match = "match"
            elif body_match == "partial" and title_match == "mismatch":
                title_match = "partial"

    return {
        "status": "alive",
        "http_code": http_code,
        "final_url": final_url,
        "page_title": page_title,
        "title_match": title_match,
        "notes": "",
    }


def body_contains_cited_title(html: str, cited_title: str) -> str:
    """
    Strip HTML tags, look for the cited title's substantive tokens in the body.

    Returns 'match' if 60%+ of substantive tokens appear in the body,
    'partial' if 30-60%, 'no' otherwise. Less strict than compare_titles
    because the body is much larger than the title.
    """
    # Strip script/style blocks first
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).lower()

    cited = re.sub(r"[^\w\s]", " ", cited_title.lower())
    stop = {"a", "an", "the", "of", "and", "or", "for", "in", "on", "at", "to",
            "with", "by", "from", "as", "is", "are", "una", "el", "la", "los",
            "las", "del", "de", "y", "o", "para", "en", "con", "por", "un",
            "le", "les", "des", "et", "ou", "pour", "how", "why", "what",
            "could", "would", "should", "not"}
    cited_tokens = [t for t in cited.split() if len(t) > 2 and t not in stop]
    if len(cited_tokens) < 2:
        return "no"

    hits = sum(1 for t in cited_tokens if t in body)
    coverage = hits / len(cited_tokens)
    if coverage >= 0.6:
        return "match"
    if coverage >= 0.3:
        return "partial"
    return "no"


def compare_titles(cited: str, fetched: str) -> str:
    """Token-overlap title comparison. Returns 'match', 'partial', or 'mismatch'."""
    def tokens(s: str) -> set[str]:
        s = re.sub(r"[^\w\s]", " ", s.lower())
        stop = {"a", "an", "the", "of", "and", "or", "for", "in", "on", "at", "to",
                "with", "by", "from", "as", "is", "are", "una", "el", "la", "los",
                "las", "del", "de", "y", "o", "para", "en", "con", "por", "un",
                "le", "les", "des", "et", "ou", "pour"}
        return {t for t in s.split() if len(t) > 2 and t not in stop}

    c_tok = tokens(cited)
    f_tok = tokens(fetched)
    if not c_tok:
        return "mismatch"
    overlap = len(c_tok & f_tok)
    coverage = overlap / len(c_tok)  # fraction of cited title's tokens present in fetched
    if coverage >= 0.6:
        return "match"
    if coverage >= 0.25:
        return "partial"
    return "mismatch"


def grumpy_verdict(bibsleuth_verdict: str, url_check: dict,
                   has_doi: bool, has_url: bool, has_candidates: bool) -> tuple[str, str]:
    """
    Combine bibsleuth verdict + URL liveness into the final Grumpy verdict.
    Returns (verdict, rationale).

    Verdicts:
      confirmed     — strong evidence the reference exists and matches the citation
      unreachable   — URL returns 4xx/5xx/timeout (could be link rot, could be fabrication)
      title-mismatch — URL alive but page title differs from cited title (chimeric smell)
      escalate      — no positive evidence; Marc must verify manually
    """
    # Academic-track first: bibsleuth verified/likely with provider hits → confirmed.
    # The academic-DB triangulation is the strong signal here; the URL check is
    # secondary. A title mismatch on a DOI URL is almost always a JS-side redirect
    # (Elsevier linkinghub, Springer link redirector, etc.) where the actual title
    # is in the JS payload we don't execute. Don't let it override bibsleuth.
    if bibsleuth_verdict in ("verified", "likely") and has_candidates:
        return "confirmed", f"bibsleuth `{bibsleuth_verdict}` with provider hits — academic-DB triangulation is authoritative"

    # URL-track: misc-with-URL — does the URL actually exist?
    if has_url:
        status = url_check.get("status")
        if status == "alive":
            tm = url_check.get("title_match")
            if tm == "match":
                return "confirmed", f"URL alive (HTTP {url_check.get('http_code')}) + page title matches cited title"
            if tm == "partial":
                return "confirmed", f"URL alive (HTTP {url_check.get('http_code')}) + page title partially matches"
            if tm == "mismatch":
                return "title-mismatch", f"URL alive but page title does NOT match cited title (page: {url_check.get('page_title','?')[:60]}) — possible chimeric reference"
            # title_match is None — couldn't extract page title
            return "confirmed", f"URL alive (HTTP {url_check.get('http_code')}) — title comparison not possible"
        if status == "dead":
            return "unreachable", f"URL returns {url_check.get('http_code')} ({url_check.get('notes')})"
        if status == "blocked":
            return "escalate", f"URL exists but request blocked (HTTP {url_check.get('http_code')}); Marc must verify manually"
        if status in ("timeout", "unreachable"):
            return "unreachable", url_check.get("notes", "URL could not be reached")

    # No URL, no DOI, no academic-DB candidates → escalate
    return "escalate", "no URL, no DOI hit, no academic-DB candidates — Marc must verify this reference manually"


def run_bibsleuth(bib_path: Path) -> dict:
    """Invoke bibsleuth, return parsed JSON report."""
    with tempfile.TemporaryDirectory() as td:
        out_base = Path(td) / "report"
        cmd = [
            "bibsleuth", "check", str(bib_path),
            "--no-llm",
            "--format", "json",
            "-o", str(out_base),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # bibsleuth uses non-zero exit codes to signal "found unverified refs",
        # not as a tool-level failure. Treat presence of the JSON output as the
        # success signal instead.
        report_path = out_base.with_suffix(".json")
        if not report_path.exists():
            for cand in [Path(td) / "report.json", out_base]:
                if cand.exists():
                    report_path = cand
                    break
        if not report_path.exists():
            sys.stderr.write(
                f"bibsleuth produced no JSON (exit {result.returncode}).\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}\n"
            )
            sys.exit(2)
        return json.loads(report_path.read_text())


def parse_existing_keys(md_path: Path) -> set[str]:
    """Return set of ref keys already present in the markdown file."""
    if not md_path.exists():
        return set()
    text = md_path.read_text()
    # Look for "## [refkey]" section markers
    return set(re.findall(r"^##\s+\[([^\]]+)\]", text, re.MULTILINE))


def parse_bib_urls_and_titles(bib_path: Path) -> dict[str, dict]:
    """
    Parse a .bib file into a dict of {entry_key: {url, title}}.

    This is a deliberately lenient parser — we only need the URL and title
    fields per entry to feed the URL-liveness step. Anything bibtexparser
    handles natively goes through bibsleuth's own parsing.
    """
    raw = bib_path.read_text()
    entries: dict[str, dict] = {}

    # Split on @type{key — keep the type+key as a header for each block
    blocks = re.split(r"\n(?=@\w+\s*\{)", raw)
    for block in blocks:
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", block)
        if not m:
            continue
        key = m.group(2).strip()

        def field(name: str) -> str | None:
            # field = {value} or field = "value", allow multiline braces
            pat = rf'\b{re.escape(name)}\s*=\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}'
            m2 = re.search(pat, block, re.IGNORECASE)
            if m2:
                return re.sub(r"\s+", " ", m2.group(1)).strip().rstrip(",").strip()
            pat2 = rf'\b{re.escape(name)}\s*=\s*"([^"]*)"'
            m3 = re.search(pat2, block, re.IGNORECASE)
            if m3:
                return re.sub(r"\s+", " ", m3.group(1)).strip()
            return None

        url = field("url") or field("howpublished")  # some misc entries put URL in howpublished
        if url:
            # Always extract via regex that stops at whitespace OR braces — handles
            # both bare `url = {https://...}` (captured content is the URL) and
            # nested `howpublished = {\url{https://...}}` (where the inner `}` of
            # \url{} would otherwise leak into the captured URL string).
            urlm = re.search(r"https?://[^\s}]+", url)
            url = urlm.group(0).rstrip(",.;)") if urlm else None

        entries[key] = {
            "url": url,
            "title": field("title"),
        }
    return entries


def best_candidate(result: dict) -> dict | None:
    """Pick the top candidate by score, falling back to first if no scores."""
    cands = result.get("candidates", [])
    if not cands:
        return None
    scored = [c for c in cands if isinstance(c.get("score"), (int, float))]
    if scored:
        return max(scored, key=lambda c: c["score"])
    return cands[0]


def fmt_authors(authors: list[str]) -> str:
    if not authors:
        return "—"
    if len(authors) <= 3:
        return ", ".join(authors)
    return f"{', '.join(authors[:3])}, et al."


def fmt_ref_block(result: dict, bib_entries: dict[str, dict]) -> tuple[str, str]:
    """
    Render one Markdown section. Returns (markdown_block, grumpy_verdict).

    bib_entries: dict from parse_bib_urls_and_titles — gives us the
    URL + title from the .bib directly, which bibsleuth does not surface.
    """
    key = result["key"]
    bib_verdict = result.get("verdict", "unknown")
    score = result.get("score")
    reasons = result.get("reasons", [])
    entry_type = result.get("entry_type", "—")
    candidate = best_candidate(result)
    has_candidates = bool(result.get("candidates"))

    doi = None
    citation_line = "(no candidate metadata found)"
    abstract_text, abstract_provider = None, None

    if candidate:
        doi = (candidate.get("ids") or {}).get("doi") or ""
        title = candidate.get("title", "—")
        authors = fmt_authors(candidate.get("authors", []))
        year = candidate.get("year", "—")
        cand_url = candidate.get("url", "")
        citation_line = f"{authors} ({year}). *{title}*."
        if cand_url:
            citation_line += f" [{cand_url}]({cand_url})"

        if doi:
            abstract_text, abstract_provider = fetch_abstract(doi)
            time.sleep(0.4)  # be polite to free APIs

    # URL liveness check — pull URL from the .bib (or fall back to DOI URL)
    bib_meta = bib_entries.get(key, {})
    bib_url = bib_meta.get("url")
    bib_title = bib_meta.get("title")
    cited_title = bib_title or (candidate.get("title") if candidate else None)
    url_to_check = bib_url or (f"https://doi.org/{doi}" if doi else None)

    url_check = {"status": "no-url", "http_code": None, "final_url": None,
                 "page_title": None, "title_match": None, "notes": ""}
    if url_to_check:
        url_check = check_url_liveness(url_to_check, cited_title)
        time.sleep(0.3)  # be polite to publishers

    # Compute the Grumpy verdict
    g_verdict, g_rationale = grumpy_verdict(
        bibsleuth_verdict=bib_verdict,
        url_check=url_check,
        has_doi=bool(doi),
        has_url=bool(url_to_check),
        has_candidates=has_candidates,
    )

    # Emoji prefixes so the human eye finds problem refs fast
    verdict_emoji = {
        "confirmed": "✅",
        "title-mismatch": "⚠️",
        "unreachable": "🚫",
        "escalate": "❓",
    }.get(g_verdict, "·")

    lines = [f"## [{key}] — {verdict_emoji} `{g_verdict}`", ""]
    lines.append(f"**Citation:** {citation_line}")
    lines.append("")
    lines.append(f"- **Grumpy verdict:** `{g_verdict}` — {g_rationale}")
    lines.append(f"- **Bibsleuth:** `{bib_verdict}`" + (f" (score {score:.2f})" if isinstance(score, (int, float)) else ""))
    lines.append(f"- **Entry type:** {entry_type}")
    if doi:
        lines.append(f"- **DOI:** [{doi}](https://doi.org/{doi})")
    if reasons:
        lines.append(f"- **Bibsleuth notes:** {'; '.join(reasons)}")

    providers_found = sorted({c.get("provider", "?") for c in result.get("candidates", []) if c.get("provider")})
    if providers_found:
        lines.append(f"- **Providers with hits:** {', '.join(providers_found)} ({len(providers_found)}/6)")

    # URL liveness section
    if url_to_check:
        status = url_check.get("status", "?")
        lines.append("")
        lines.append(f"**URL check** — `{status}` (HTTP {url_check.get('http_code') or '—'})")
        lines.append(f"- **URL checked:** <{url_to_check}>")
        if url_check.get("final_url") and url_check["final_url"] != url_to_check:
            lines.append(f"- **Redirected to:** <{url_check['final_url']}>")
        if url_check.get("page_title"):
            lines.append(f"- **Page title:** *{url_check['page_title'][:200]}*")
            if url_check.get("title_match"):
                lines.append(f"- **Title match:** `{url_check['title_match']}` (cited title vs. page title)")
        if url_check.get("notes"):
            lines.append(f"- **Notes:** {url_check['notes']}")

    lines.append("")
    if abstract_text:
        lines.append(f"**Abstract** (via {abstract_provider}):")
        lines.append("")
        # Wrap abstract as a blockquote, keep paragraphing intact
        for para in abstract_text.split("\n"):
            lines.append(f"> {para.strip()}" if para.strip() else "> ")
        lines.append("")
    else:
        lines.append("**Abstract:** *not retrievable from semantic_scholar / openalex / crossref.*")
        lines.append("")

    # Placeholders for Grumpy's manual claim-checking pass
    lines.append("**Cited in paper at:** _(Grumpy: fill in section / page)_")
    lines.append("")
    lines.append("**Claim made:** _(Grumpy: what the reviewed paper says about this reference)_")
    lines.append("")
    lines.append("**Assessment:** _(Grumpy: supported / partially supported / unsupported / claim is generic / no full-text access)_")
    lines.append("")
    lines.append("**Flags:** _(manual: anything else)_")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines), g_verdict


def fmt_header(bib_path: Path, report: dict) -> str:
    cfg = report.get("config", {})
    providers = ", ".join(cfg.get("providers", []))
    summary = report.get("summary", {})
    summary_line = ", ".join(f"{v} {k}" for k, v in summary.items())
    return "\n".join([
        f"# Reference verification — `{bib_path.name}`",
        "",
        f"**Source:** `{bib_path}`",
        f"**Generated:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"**bibsleuth version:** {report.get('version', '?')}",
        f"**Providers consulted:** {providers}",
        f"**Summary:** {summary_line}",
        "",
        "> [!info]",
        "> This file is the **source of truth** for reference validation on this document. Subsequent reviews read this file rather than re-running bibsleuth. Grumpy fills in *Cited in paper at*, *Claim made*, and *Assessment* per reference after comparing the citing paper's claim to the cited paper's abstract.",
        "",
        "---",
        "",
    ])


def fmt_escalation_summary(verdict_counts: dict[str, int],
                           escalations: list[tuple[str, str]],
                           unreachables: list[tuple[str, str]],
                           mismatches: list[tuple[str, str]]) -> str:
    """Render a top-of-file summary section that surfaces blockers fast."""
    total = sum(verdict_counts.values())
    confirmed = verdict_counts.get("confirmed", 0)
    lines = [
        "## Submission gate — Grumpy verdict roll-up",
        "",
        f"**{confirmed} / {total} references confirmed.** Per rule §14: a paper does not ship until every reference is `confirmed`.",
        "",
        "| Verdict | Count | Meaning |",
        "|---|---:|---|",
        f"| ✅ `confirmed`    | {verdict_counts.get('confirmed', 0):>3} | bibsleuth verified/likely **or** URL alive + title match |",
        f"| ⚠️ `title-mismatch` | {verdict_counts.get('title-mismatch', 0):>3} | URL exists but page title doesn't match the cited title — possible chimeric ref |",
        f"| 🚫 `unreachable`  | {verdict_counts.get('unreachable', 0):>3} | URL returns 4xx/5xx/timeout — link rot or fabrication |",
        f"| ❓ `escalate`     | {verdict_counts.get('escalate', 0):>3} | no positive evidence — **Marc must verify manually** |",
        "",
    ]

    if mismatches:
        lines.append("### ⚠️ Title-mismatch — chimeric smell, inspect each one")
        lines.append("")
        for key, rationale in mismatches:
            lines.append(f"- **`[{key}]`** — {rationale}")
        lines.append("")

    if unreachables:
        lines.append("### 🚫 Unreachable URLs — link rot or fabrication")
        lines.append("")
        for key, rationale in unreachables:
            lines.append(f"- **`[{key}]`** — {rationale}")
        lines.append("")

    if escalations:
        lines.append("### ❓ Refs Marc must confirm manually")
        lines.append("")
        lines.append("Bibsleuth can't reach these, and there's no URL/DOI to mechanically check. Confirm each one exists (publisher page, ISBN, archive snapshot, etc.) and either upgrade the bib entry with a verifiable URL/DOI, or remove the citation.")
        lines.append("")
        for key, rationale in escalations:
            lines.append(f"- **`[{key}]`** — {rationale}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("bib", type=Path, help="Path to the .bib file under review")
    ap.add_argument("--output", "-o", type=Path, default=None,
                    help="Output markdown path. Defaults to <bib-stem>-refs-checks.md alongside the .bib.")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite the output file even if it already exists. Use when the verdict-computation logic changes.")
    args = ap.parse_args()

    bib_path: Path = args.bib.resolve()
    if not bib_path.exists():
        sys.stderr.write(f"bib file not found: {bib_path}\n")
        return 1

    out_path: Path = args.output if args.output else bib_path.parent / f"{bib_path.stem}-refs-checks.md"
    out_path = out_path.resolve()

    print(f"→ bibsleuth on {bib_path.name} …", file=sys.stderr)
    report = run_bibsleuth(bib_path)
    bib_entries = parse_bib_urls_and_titles(bib_path)
    print(f"→ parsed {len(bib_entries)} bib entries for URL/title metadata", file=sys.stderr)

    existing_keys = set() if args.force else parse_existing_keys(out_path)
    if existing_keys:
        print(f"→ {len(existing_keys)} ref(s) already in {out_path.name}; appending only new entries", file=sys.stderr)
    elif args.force and out_path.exists():
        print(f"→ --force: regenerating {out_path.name} from scratch", file=sys.stderr)

    results = report.get("results", [])
    new_results = [r for r in results if r["key"] not in existing_keys]
    print(f"→ {len(new_results)} new ref(s) to process (of {len(results)} total)", file=sys.stderr)

    # Process all entries, collecting verdicts for the rollup section
    verdict_counts: dict[str, int] = {}
    escalations: list[tuple[str, str]] = []
    unreachables: list[tuple[str, str]] = []
    mismatches: list[tuple[str, str]] = []
    blocks: list[str] = []
    for i, r in enumerate(new_results, start=1):
        print(f"  [{i}/{len(new_results)}] {r['key']} … ", end="", file=sys.stderr, flush=True)
        block, g_verdict = fmt_ref_block(r, bib_entries)
        blocks.append(block)
        verdict_counts[g_verdict] = verdict_counts.get(g_verdict, 0) + 1
        # Extract the per-ref rationale from the first non-blank line of the block
        rationale_match = re.search(r"- \*\*Grumpy verdict:\*\* `[^`]+` — (.+)", block)
        rationale = rationale_match.group(1).strip() if rationale_match else ""
        if g_verdict == "escalate":
            escalations.append((r["key"], rationale))
        elif g_verdict == "unreachable":
            unreachables.append((r["key"], rationale))
        elif g_verdict == "title-mismatch":
            mismatches.append((r["key"], rationale))
        print(g_verdict, file=sys.stderr)

    # Compose output: header → submission-gate rollup → per-ref blocks
    if args.force or not existing_keys:
        with out_path.open("w") as fh:
            fh.write(fmt_header(bib_path, report))
            fh.write(fmt_escalation_summary(verdict_counts, escalations, unreachables, mismatches))
            for block in blocks:
                fh.write(block)
    else:
        # Append mode — just add the new blocks (no rollup regeneration; that's
        # the limitation of append mode. Use --force after adding many refs.)
        with out_path.open("a") as fh:
            for block in blocks:
                fh.write(block)

    print(f"\n→ wrote {out_path}", file=sys.stderr)
    print(f"→ verdict tally: {dict(verdict_counts)}", file=sys.stderr)
    if escalations:
        print(f"→ {len(escalations)} ref(s) need Marc's manual confirmation — see top of file", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
