#!/usr/bin/env python3
"""tools/wiki/classify_persons.py — tag person entries with role categories.

Multi-tag (not single-category) classification. A single person can be
`contact`, `co-author`, `inner-circle`, all at once. Default (no roles)
means `cited` — extracted from sources but not a Marc-connected person.

Auto-derived roles:
  contact     — slug or alias matches an entry in inbox/lore/persons/
  co-author   — appears in the `authors:` field of any meta.json under
                sources/shared/papers-own-archive/. Matched against wiki
                slugs by last-name token (Marc's first paper used
                "Last, First-initials" citation style; full-name slugs
                in the wiki need fuzzy resolution on the last name).

Manual role:
  inner-circle — hardcoded slug list at top of this file. Edit and rerun
                 to add/remove members.

Re-runnable. Idempotent: replaces existing roles: frontmatter rather than
appending.

Usage:
  python3 tools/wiki/classify_persons.py            # write + report
  python3 tools/wiki/classify_persons.py --dry-run  # report only
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI_PERSONS = REPO / "wiki" / "persons"
BILBY_PERSONS = REPO / "inbox" / "lore" / "persons"
MARC_AUTHOR_META_GLOB = "sources/shared/papers-own-archive/*/*/meta.json"
MARC_NAME_TOKENS = {"alier", "ludo"}  # excluded from co-author set

# Manual inner-circle list. Marc-named slugs. Edit and rerun to update.
# Marc 2026-05-12: named Sé, Juanan, Fran, Faraón and "others" — initial
# guesses, to refine. `s-...` initial-only entries dropped (no clear
# match for "Sé"); Marc to specify the canonical slug.
INNER_CIRCLE: set[str] = {
    "faraon-llorens-largo",   # Faraón Llorens-Largo, edtech researcher
    "fran-rodriguez",         # Fran Rodriguez, UPCNet/IthinkUPC
    "juanan-pereira",         # Juanan Pereira (also has slug variants juanan-pe, juananpe)
    # Sé: TODO — Marc to name
    # Others: TODO — Marc to extend
}


def load_bilby_contacts() -> set[str]:
    """Return the set of contact slugs from inbox/lore/persons/."""
    if not BILBY_PERSONS.exists():
        return set()
    return {p.stem for p in BILBY_PERSONS.glob("*.md")}


def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def load_coauthor_records() -> list[tuple[str, str]]:
    """Return list of (last_name_token, initials_string) from Marc's
    own-archive paper meta.json files.

    "Casany, M.J." → ("casany", "mj")
    "García-Holgado, A." → ("garciaholgado", "a")  (compound last name normalized)
    """
    out: list[tuple[str, str]] = []
    for meta_path in REPO.glob(MARC_AUTHOR_META_GLOB):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for author in (meta.get("authors") or "").split(";"):
            author = author.strip()
            if not author or "," not in author:
                continue
            last_raw, first_raw = author.split(",", 1)
            last = _strip_accents(last_raw).strip().lower()
            last = re.sub(r"[^a-z]+", "", last)  # collapse hyphens / spaces
            if not last or last in MARC_NAME_TOKENS:
                continue
            initials = re.sub(r"[^a-z]+", "", _strip_accents(first_raw).strip().lower())
            out.append((last, initials))
    return out


def _slug_initials_match(slug: str, last: str, initials: str) -> bool:
    """Does this slug correspond to a person 'Last, Initials' from meta.json?

    Spanish/Catalan compound names: a wiki slug may be `first-surname1-surname2`
    where the meta.json only carries `surname1` (e.g. `faraon-llorens-largo`
    against meta "Llorens, F."). Scans the slug for any contiguous run of
    tokens that joins to `last`; for each match position, treats the tokens
    BEFORE the match as the first-name part and compares initials.
    """
    if not initials:
        return False
    parts = slug.split("-")
    for start in range(len(parts)):
        for n in range(1, min(4, len(parts) - start) + 1):
            run = parts[start : start + n]
            if "".join(run) != last:
                continue
            first_tokens = parts[:start]
            if not first_tokens:
                return False
            slug_initials = "".join(t[0] for t in first_tokens if t)
            if (
                slug_initials.startswith(initials)
                or initials.startswith(slug_initials)
            ):
                return True
    return False


def slug_tokens(slug: str) -> set[str]:
    return set(t for t in slug.split("-") if t)


def resolve_coauthor_slugs(
    coauthor_records: list[tuple[str, str]], wiki_slugs: list[str]
) -> tuple[set[str], dict[str, list[str]], dict[str, list[str]]]:
    """For each (last_name, initials) record, find wiki slugs that match.

    Returns:
      - matched: set of slugs definitively tagged as co-author
      - ambiguous: {last_name: [candidate_slugs]} — last names where
        first-initial filtering left multiple candidates (over-tag bucket)
      - unmatched: {last_name: [seen_initials]} — meta.json authors with
        no corresponding wiki entry (gap to surface)
    """
    matched: set[str] = set()
    ambiguous: dict[str, list[str]] = {}
    unmatched: dict[str, list[str]] = defaultdict(list)

    # group records by last name to handle multi-paper co-authors
    by_last: dict[str, set[str]] = defaultdict(set)
    for last, initials in coauthor_records:
        by_last[last].add(initials)

    for last, initials_set in by_last.items():
        # First, find any candidate slugs that contain `last` as a substring
        # of a token (handles both single-token "casany" and compound "garcia-holgado")
        candidates_loose = [
            s for s in wiki_slugs
            if last in s.replace("-", "")
            and any(t for t in s.split("-") if last.startswith(t) or t.startswith(last) or last in t)
        ]
        if not candidates_loose:
            unmatched[last] = sorted(initials_set)
            continue

        # Apply first-initial filter
        for initials in initials_set:
            confirmed = [s for s in candidates_loose if _slug_initials_match(s, last, initials)]
            if len(confirmed) == 1:
                matched.add(confirmed[0])
            elif len(confirmed) > 1:
                matched.update(confirmed)
                ambiguous.setdefault(f"{last}/{initials}", confirmed)

    return matched, ambiguous, unmatched


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """Return (frontmatter_dict, frontmatter_block, body). Minimal YAML parser
    — only the fields we need (name, aliases, roles, sources_count)."""
    if not text.startswith("---\n"):
        return {}, "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, "", text
    block = text[4:end]
    body = text[end + 5 :]
    fm: dict = {}
    in_aliases = False
    in_roles = False
    aliases: list[str] = []
    roles: list[str] = []
    for line in block.split("\n"):
        if not line.strip():
            in_aliases = in_roles = False
            continue
        if line.startswith("aliases:"):
            in_aliases = True
            in_roles = False
            continue
        if line.startswith("roles:"):
            in_roles = True
            in_aliases = False
            continue
        if in_aliases:
            m = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if m:
                aliases.append(m.group(1).strip("\"'"))
                continue
            in_aliases = False
        if in_roles:
            m = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if m:
                roles.append(m.group(1).strip("\"'"))
                continue
            in_roles = False
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("\"'")
    fm["aliases"] = aliases
    fm["roles"] = roles
    return fm, block, body


def render_frontmatter(fm: dict, original_block: str, roles: list[str]) -> str:
    """Update the roles: section in the frontmatter block. Preserves all other
    fields and their order. Replaces existing roles: block or appends after
    last frontmatter field."""
    lines = original_block.split("\n")
    out: list[str] = []
    i = 0
    roles_block = ["roles:"] + [f"  - {r}" for r in roles]
    written = False
    while i < len(lines):
        line = lines[i]
        if line.startswith("roles:"):
            # Skip existing roles block
            out.extend(roles_block)
            written = True
            i += 1
            while i < len(lines) and re.match(r"^\s+-\s+", lines[i]):
                i += 1
            continue
        out.append(line)
        i += 1
    if not written and roles:
        # Append at end of frontmatter
        out.extend(roles_block)
    return "---\n" + "\n".join(out) + "\n---\n"


def source_paths_from_body(body: str) -> list[str]:
    """Pull source path strings from Timeline / Sources lines in the body."""
    paths = re.findall(r"\[\[([^\]]+\.md)\]\]", body)
    return paths


def classify_one(
    person_path: Path, contacts: set[str], coauthor_slugs: set[str]
) -> tuple[list[str], dict]:
    text = person_path.read_text(encoding="utf-8")
    fm, fm_block, body = parse_frontmatter(text)
    slug = fm.get("slug") or person_path.stem
    aliases = fm.get("aliases", [])
    roles: list[str] = []

    # contact: slug or any alias matches a Bilby contact slug
    candidates = {slug, *aliases}
    if candidates & contacts:
        roles.append("contact")

    # co-author: slug appears in the set resolved from meta.json author lists
    if slug in coauthor_slugs:
        roles.append("co-author")

    # inner-circle: slug in hardcoded list
    if slug in INNER_CIRCLE:
        roles.append("inner-circle")

    new_text = render_frontmatter(fm, fm_block, roles) + body
    return roles, {"path": person_path, "new_text": new_text, "old_text": text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report only, no writes")
    args = ap.parse_args()

    contacts = load_bilby_contacts()
    print(f"loaded {len(contacts)} bilby contacts from inbox/lore/persons/")

    coauthor_records = load_coauthor_records()
    wiki_slugs = sorted({p.stem for p in WIKI_PERSONS.glob("*.md") if p.name != "INDEX.md"})
    coauthor_slugs, ambiguous, unmatched = resolve_coauthor_slugs(coauthor_records, wiki_slugs)
    print(
        f"co-author meta.json scan: {len(coauthor_records)} author records "
        f"resolved to {len(coauthor_slugs)} wiki slugs "
        f"({len(ambiguous)} ambiguous after initials filter, "
        f"{len(unmatched)} meta authors with no wiki entry)"
    )
    print(f"inner-circle list: {len(INNER_CIRCLE)} slugs")

    results = defaultdict(list)
    writes = 0
    for person_path in sorted(WIKI_PERSONS.glob("*.md")):
        if person_path.name in ("INDEX.md",):
            continue
        roles, payload = classify_one(person_path, contacts, coauthor_slugs)
        bucket = "+".join(roles) if roles else "cited"
        results[bucket].append(person_path.stem)
        if payload["new_text"] != payload["old_text"]:
            if not args.dry_run:
                person_path.write_text(payload["new_text"], encoding="utf-8")
            writes += 1

    print()
    print(f"{'classification':<35} {'count':>6}")
    print("-" * 45)
    for bucket in sorted(results, key=lambda k: (-len(results[k]), k)):
        print(f"{bucket:<35} {len(results[bucket]):>6}")
    print("-" * 45)
    print(f"{'TOTAL persons':<35} {sum(len(v) for v in results.values()):>6}")
    print()
    print(f"frontmatter writes: {writes}{' (dry-run, skipped)' if args.dry_run else ''}")

    # Surface inner-circle members and any misses
    print()
    print("inner-circle members (found in wiki/persons/):")
    for slug in sorted(INNER_CIRCLE):
        path = WIKI_PERSONS / f"{slug}.md"
        marker = "✓" if path.exists() else "MISSING"
        print(f"  {marker}  {slug}")

    # Surface contacts that have NO matching wiki entry (interesting gaps)
    wiki_slugs = {p.stem for p in WIKI_PERSONS.glob("*.md")}
    wiki_aliases: set[str] = set()
    for p in WIKI_PERSONS.glob("*.md"):
        fm, _, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        wiki_aliases.update(fm.get("aliases", []))
    orphan_contacts = sorted(contacts - set(wiki_slugs) - wiki_aliases)
    print()
    print(f"bilby contacts with no matching wiki entry: {len(orphan_contacts)}")
    for slug in orphan_contacts[:15]:
        print(f"  · {slug}")
    if len(orphan_contacts) > 15:
        print(f"  · ... ({len(orphan_contacts) - 15} more)")

    if ambiguous:
        print()
        print(f"ambiguous after initials filter (matched > 1 wiki slug):")
        for key, candidates in sorted(ambiguous.items())[:10]:
            print(f"  · {key}: {', '.join(candidates)}")
        if len(ambiguous) > 10:
            print(f"  · ... ({len(ambiguous) - 10} more)")

    if unmatched:
        print()
        print(f"meta.json co-authors without a wiki entry: {len(unmatched)}")
        for last, initials_list in sorted(unmatched.items())[:10]:
            print(f"  · {last} ({', '.join(initials_list)})")
        if len(unmatched) > 10:
            print(f"  · ... ({len(unmatched) - 10} more)")


if __name__ == "__main__":
    main()
