#!/usr/bin/env python3
"""Build a small public package inventory from a private R-universe API snapshot.

Run from the project root. Only selected package/build fields reach the outputs;
the raw API response, contacts, commit metadata, and other metadata stay private.
"""

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlparse


SNAPSHOT_DATE = "2026-09-29"
UNIVERSE = "https://jimianelli.r-universe.dev"
FIELDS = (
    "package", "title", "available_version", "attempted_version", "record_type",
    "reported_build_status", "source_check", "check_summary", "upstream_url",
    "r_universe_url", "build_log_url", "snapshot_date",
)


def text(value):
    return " ".join(str(value).split()) if value is not None else ""


def url(value):
    value = text(value)
    parsed = urlparse(value)
    if value and (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password):
        raise ValueError("Inventory link must be an HTTPS URL without credentials")
    return value


def reduce_package(source):
    name = text(source.get("Package"))
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9.]*", name):
        raise ValueError("Unexpected package name")
    failure = source.get("_failure") or {}
    failed_record = source.get("_type") == "failure"
    jobs = source.get("_jobs") or ([failure["job"]] if failure.get("job") else [])
    counts = Counter(text(job.get("check")) or "Unavailable" for job in jobs)
    source_checks = sorted({text(job.get("check")) or "Unavailable" for job in jobs if job.get("config") == "source"})
    return {
        "package": name,
        "title": text(source.get("Title")) or "Title unavailable in API snapshot",
        "available_version": "" if failed_record else text(source.get("Version")),
        "attempted_version": text(failure.get("version")),
        "record_type": "Failed source attempt" if failed_record else "Source package record",
        "reported_build_status": "failure" if failed_record else text(source.get("_status")) or "unavailable",
        "source_check": ", ".join(source_checks) or "Unavailable",
        "check_summary": "; ".join(f"{key}: {counts[key]}" for key in sorted(counts)) or "Unavailable",
        "upstream_url": url(source.get("_upstream")),
        "r_universe_url": f"{UNIVERSE}/{quote(name)}",
        "build_log_url": url(source.get("_buildurl") or failure.get("buildurl")),
        "snapshot_date": SNAPSHOT_DATE,
    }


def make_link(link, label, package):
    if not link:
        return html.escape(f"{label} unavailable")
    return f'<a href="{html.escape(link, quote=True)}" aria-label="{html.escape(label + " for " + package, quote=True)}">{html.escape(label)}</a>'


def make_row(package):
    esc = html.escape
    name = package["package"]
    versions = []
    if package["available_version"]:
        versions.append(f'<span class="version">{esc(package["available_version"])}</span><span class="detail">Available source record</span>')
    if package["attempted_version"]:
        versions.append(f'<span class="version">{esc(package["attempted_version"])}</span><span class="detail">Attempted version</span>')
    if not versions:
        versions.append("Version unavailable")
    status = package["reported_build_status"]
    badge_class = "failure" if status == "failure" else "success" if status == "success" else "unknown"
    links = " ".join(make_link(package[key], label, name) for key, label in (
        ("r_universe_url", "R-universe"), ("upstream_url", "Upstream"), ("build_log_url", "Build logs")
    ))
    return f'''<tr data-package="{esc(name, quote=True)}" data-status="{esc(status, quote=True)}">
<th scope="row">{esc(name)}</th>
<td>{"".join(versions)}</td>
<td class="package-title">{esc(package["title"])}</td>
<td><span class="badge {badge_class}">{esc(status.capitalize())}</span><span class="detail">{esc(package["record_type"])}</span></td>
<td><strong>Source: {esc(package["source_check"])}</strong><span class="detail">All reported jobs: {esc(package["check_summary"])}</span></td>
<td class="links">{links}</td>
</tr>'''


def make_page(packages):
    rows = "\n".join(make_row(p) for p in packages)
    count = len(packages)
    available = sum(bool(p["available_version"]) for p in packages)
    attempts = sum(p["record_type"] == "Failed source attempt" for p in packages)
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Jim's R-universe package inventory with source versions, build status, checks, and project links.">
<title>R Packages · Jim's Project Hub</title>
<style>
:root{--bg:#f0f2f5;--card-bg:#fff;--header:#3a4a5c;--accent:#205f9d;--radius:10px;--shadow:0 2px 8px rgba(0,0,0,.10)}
*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:#222;line-height:1.5;margin:0 auto;max-width:1400px;padding:32px 24px 48px}
a{color:var(--accent);text-underline-offset:3px}a:focus-visible,input:focus-visible,select:focus-visible,.table-wrap:focus-visible{outline:3px solid #805500;outline-offset:4px}
.skip{position:absolute;top:-70px;left:20px;background:#fff;padding:8px 16px;z-index:10}.skip:focus{top:10px}
header{border-bottom:2px solid #dde0e8;padding-bottom:20px;margin-bottom:24px}h1{font-size:1.9rem;letter-spacing:-.02em;color:var(--header);margin:0 0 8px}h2{font-size:1.1rem;color:var(--header);margin-top:0}p{margin:8px 0 14px}nav{display:flex;flex-wrap:wrap;gap:10px 24px;margin-bottom:24px}nav a[aria-current]{font-weight:700;text-decoration:none;color:var(--header)}
.summary{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}.summary p{background:var(--card-bg);box-shadow:var(--shadow);border-radius:var(--radius);border-top:4px solid #3e7fc1;padding:14px 18px;margin:0;min-width:190px}.summary strong{display:block;font-size:1.65rem;color:var(--header)}
.guide{max-width:1050px}.filters{display:flex;gap:16px;flex-wrap:wrap;align-items:end;margin:24px 0 12px}.filters label{font-weight:650;display:block;margin-bottom:5px}.filters input,.filters select{font:inherit;min-height:44px;border:1px solid #65717e;border-radius:6px;padding:8px 12px;background:white;color:#222}.filters input{width:min(430px,85vw)}
.table-wrap{background:white;border-radius:var(--radius);box-shadow:var(--shadow);overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:970px;text-align:left}caption{text-align:left;padding:18px;font-weight:650;color:var(--header)}thead{background:var(--header);color:white}th,td{padding:14px 12px;vertical-align:top;border-bottom:1px solid #dce1e7}th[scope=row]{font-size:.95rem;overflow-wrap:anywhere}tbody tr:last-child>*{border-bottom:none}tbody tr:nth-child(even){background:#f7f9fc}.package-title{min-width:240px;max-width:390px;font-size:.92rem}.version{font-family:ui-monospace,monospace}.detail{display:block;font-size:.82rem;color:#4c5966;margin-top:5px}.badge{display:inline-block;font-weight:650;font-size:.85rem;padding:2px 9px;border-radius:5px}.success{background:#dceee2;color:#215335}.failure{background:#f8dfe0;color:#7a2429}.unknown{background:#e6e9ee;color:#374450}.links a{display:block;white-space:nowrap;margin-bottom:8px}.downloads{display:flex;gap:20px;flex-wrap:wrap}.footer{margin-top:32px;border-top:1px solid #ccd2db;padding-top:16px;color:#4c5966;font-size:.9rem}[hidden]{display:none!important}
@media(max-width:650px){body{padding:22px 14px 36px}h1{font-size:1.6rem}.summary p{flex:1;min-width:140px}.filters>*{width:100%}.filters input,.filters select{width:100%}}@media print{body{background:white;padding:0;font-size:10pt;max-width:none}.filters,nav,.skip{display:none}.table-wrap{overflow:visible;box-shadow:none}table{min-width:0}th,td{padding:6px}.package-title{min-width:0}a{color:#222}.summary p{box-shadow:none;border:1px solid #aaa}.badge{background:white;color:#222}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to package inventory</a>
<header>
<nav aria-label="Project navigation"><a href="index.html">Home</a><a href="kanban.html">Kanban</a><a href="project_log.html">Project log</a><a href="packages.html" aria-current="page">R packages</a></nav>
<h1>R package inventory</h1>
<p>All packages listed in <a href="https://jimianelli.r-universe.dev/packages">Jim's R-universe</a>, captured on <time datetime="2026-09-29">September 29, 2026</time>.</p>
</header>
<main id="main">
<div class="summary" aria-label="Snapshot counts">
<p><strong>__COUNT__</strong>Packages listed</p><p><strong>__AVAILABLE__</strong>Available source records</p><p><strong>__ATTEMPTS__</strong>Failed source attempts</p>
</div>
<section class="guide" aria-labelledby="reading"><h2 id="reading">Reading the inventory</h2>
<p>Versions under “Available source record” come from package metadata. “Attempted version” comes from a failed build record. Source-provided titles are preserved; missing titles are marked explicitly.</p>
<p>Build status is the status reported by R-universe. Checks summarize the source job and all reported platform jobs, so a successful source record can still have errors on some platforms. These are software build results; scientific validation requires separate evidence.</p>
<p>Use the build logs for details. This page is a dated snapshot; package links open the current records.</p></section>
<div class="filters" id="filters" hidden>
<div><label for="search">Search packages, titles, versions, or checks</label><input id="search" type="search" autocomplete="off" placeholder="For example: pollock or ERROR" aria-controls="package-body"></div>
<div><label for="build-filter">Reported build status</label><select id="build-filter" aria-controls="package-body"><option value="">All statuses</option><option value="failure">Failure</option><option value="success">Success</option><option value="unavailable">Unavailable</option></select></div>
</div>
<p id="result-count" role="status" aria-live="polite">Showing __COUNT__ of __COUNT__ packages.</p>
<div class="table-wrap" tabindex="0" role="region" aria-label="Package table; scroll horizontally on narrow screens">
<table><caption>R-universe package and build inventory · 2026-09-29</caption>
<thead><tr><th scope="col">Package</th><th scope="col">Version</th><th scope="col">Source title</th><th scope="col">Reported build status</th><th scope="col">Checks</th><th scope="col">Links</th></tr></thead>
<tbody id="package-body">
__ROWS__
</tbody></table></div>
<p id="empty" hidden>No packages match these filters. Clear the search or choose all statuses.</p>
<p class="downloads"><a href="data/packages.csv" download>Download inventory CSV</a><a href="data/packages.json" download>Download inventory JSON</a></p>
</main>
<footer class="footer">Source: <a href="https://jimianelli.r-universe.dev/api/packages">R-universe package API</a>. Snapshot: 2026-09-29. Package titles and build fields are reduced from the source response.</footer>
<script>
(() => {
  const rows = [...document.querySelectorAll('#package-body tr')];
  const search = document.querySelector('#search');
  const status = document.querySelector('#build-filter');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty');
  function filter() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\\s+/).filter(Boolean);
    let shown = 0;
    rows.forEach(row => {
      const haystack = row.textContent.toLocaleLowerCase();
      row.hidden = !terms.every(term => haystack.includes(term)) || (status.value !== '' && row.dataset.status !== status.value);
      if (!row.hidden) shown += 1;
    });
    count.textContent = `Showing ${shown} of ${rows.length} packages.`;
    empty.hidden = shown !== 0;
  }
  search.addEventListener('input', filter);
  status.addEventListener('change', filter);
  document.querySelector('#filters').hidden = false;
})();
</script>
</body>
</html>
'''.replace("__COUNT__", str(count)).replace("__AVAILABLE__", str(available)).replace("__ATTEMPTS__", str(attempts)).replace("__ROWS__", rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default="data/r-universe-source.json")
    args = parser.parse_args()
    source = json.loads(Path(args.source).read_text(encoding="utf-8"))
    if not isinstance(source, list):
        raise ValueError("Expected a list of package API records")
    packages = sorted((reduce_package(p) for p in source), key=lambda p: p["package"].casefold())
    if len({p["package"].casefold() for p in packages}) != len(packages):
        raise ValueError("Duplicate package names")
    reduced = json.dumps(packages, indent=2, ensure_ascii=False) + "\n"
    if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", reduced):
        raise ValueError("Contact address detected in reduced output")
    page = make_page(packages)
    Path("data").mkdir(exist_ok=True)
    Path("data/packages.json").write_text(reduced, encoding="utf-8")
    with Path("data/packages.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(packages)
    Path("packages.html").write_text(page, encoding="utf-8")
    print(f"Built {len(packages)} unique package rows; {sum(bool(p['available_version']) for p in packages)} available source records; {sum(p['record_type'] == 'Failed source attempt' for p in packages)} failed source attempts.")


if __name__ == "__main__":
    main()
