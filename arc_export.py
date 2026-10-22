#!/usr/bin/env python3
"""Export Arc Browser sidebar tabs and folders to a Netscape bookmarks HTML file."""

import argparse
import html
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

SIDEBAR_FILE = "StorableSidebar.json"


def default_sidebar_path():
    if sys.platform == "win32":
        packages = Path(os.environ.get("LOCALAPPDATA", "~/AppData/Local")).expanduser() / "Packages"
        for pkg in sorted(packages.glob("TheBrowserCompany.Arc*")):
            candidate = pkg / "LocalCache" / "Local" / "Arc" / SIDEBAR_FILE
            if candidate.exists():
                return candidate
        return packages / "TheBrowserCompany.Arc" / "LocalCache" / "Local" / "Arc" / SIDEBAR_FILE
    return Path("~/Library/Application Support/Arc").expanduser() / SIDEBAR_FILE


def find_sidebar_file(explicit):
    path = explicit or default_sidebar_path()
    if not path.is_file():
        sys.exit(f"error: can't find {path}\n"
                 f"Is Arc installed? You can point to the file with --input.")
    return path


def iter_profiles(data):
    """Yield (items_by_id, spaces) for every sidebar container that holds tabs."""
    sidebar = data.get("sidebar") if isinstance(data, dict) else None
    for container in (sidebar or {}).get("containers") or []:
        if isinstance(container, dict) and "spaces" in container and "items" in container:
            items = {i["id"]: i for i in container["items"] or [] if isinstance(i, dict) and "id" in i}
            spaces = [s for s in container["spaces"] or [] if isinstance(s, dict)]
            yield items, spaces


def space_roots(space):
    """newContainerIDs alternates a {"pinned"/"unpinned": ...} marker with the root item id."""
    ids = space.get("newContainerIDs") or []
    for marker, root_id in zip(ids, ids[1:]):
        if isinstance(marker, dict) and isinstance(root_id, str):
            if "pinned" in marker:
                yield root_id, True
            elif "unpinned" in marker:
                yield root_id, False


def build_tree(root_id, items, children_of, seen=None):
    seen = seen if seen is not None else set()
    nodes = []
    for child_id in children_of.get(root_id, []):
        if child_id in seen:
            continue
        seen.add(child_id)
        item = items[child_id]
        tab = (item.get("data") or {}).get("tab")
        if isinstance(tab, dict):
            url = tab.get("savedURL") or ""
            if url:
                title = item.get("title") or tab.get("savedTitle") or url
                nodes.append({"title": title, "url": url})
        else:
            children = build_tree(child_id, items, children_of, seen)
            if children:
                nodes.append({"title": item.get("title") or "Untitled folder", "children": children})
    return nodes


def collect(data, include_unpinned):
    profiles = []
    for items, spaces in iter_profiles(data):
        children_of = defaultdict(list)
        for item_id, item in items.items():
            children_of[item.get("parentID")].append(item_id)
        # Arc stores sibling order on the parent; fall back to file order otherwise.
        for parent_id, kids in children_of.items():
            order = items.get(parent_id, {}).get("childrenIds")
            if order:
                rank = {k: n for n, k in enumerate(order)}
                kids.sort(key=lambda k: rank.get(k, len(rank)))

        folders = []
        for n, space in enumerate(spaces, 1):
            name = space.get("title") or f"Space {n}"
            for root_id, pinned in sorted(space_roots(space), key=lambda r: not r[1]):
                if not pinned and not include_unpinned:
                    continue
                tree = build_tree(root_id, items, children_of)
                if tree:
                    folders.append({"title": name if pinned else f"{name} (unpinned)", "children": tree})
        if folders:
            profiles.append(folders)

    if len(profiles) == 1:
        return profiles[0]
    return [{"title": f"Profile {n}", "children": f} for n, f in enumerate(profiles, 1)]


def count_links(nodes):
    return sum(count_links(n["children"]) if "children" in n else 1 for n in nodes)


def to_netscape_html(nodes):
    out = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
    ]

    def emit(nodes, depth):
        pad = "\t" * depth
        for node in nodes:
            title = html.escape(node["title"], quote=False)
            if "children" in node:
                out.append(f'{pad}<DT><H3>{title}</H3>')
                out.append(f"{pad}<DL><p>")
                emit(node["children"], depth + 1)
                out.append(f"{pad}</DL><p>")
            else:
                url = html.escape(node["url"], quote=True)
                out.append(f'{pad}<DT><A HREF="{url}">{title}</A>')

    emit(nodes, 1)
    out.append("</DL><p>")
    return "\n".join(out) + "\n"


def print_summary(nodes, depth=0):
    for node in nodes:
        if "children" in node:
            print(f"{'  ' * depth}{node['title']}: {count_links(node['children'])}", file=sys.stderr)
            if depth == 0 and node["title"].startswith("Profile "):
                print_summary(node["children"], depth + 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-i", "--input", type=Path, help=f"path to {SIDEBAR_FILE} (default: Arc's data folder)")
    ap.add_argument("-o", "--output", type=Path, help="output file (default: arc-bookmarks-YYYY-MM-DD.html)")
    ap.add_argument("--unpinned", action="store_true", help="also export unpinned tabs")
    ap.add_argument("--dry-run", action="store_true", help="show what would be exported, write nothing")
    ap.add_argument("-q", "--quiet", action="store_true", help="only print errors")
    args = ap.parse_args()

    source = find_sidebar_file(args.input)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"error: {source} is not valid JSON ({e})")

    nodes = collect(data, args.unpinned)
    total = count_links(nodes)
    if not total:
        sys.exit("error: no bookmarks found" + ("" if args.unpinned else " (try --unpinned)"))

    if args.dry_run or not args.quiet:
        print_summary(nodes)
    if args.dry_run:
        print(f"{total} bookmarks (dry run, nothing written)", file=sys.stderr)
        return

    output = args.output or Path(f"arc-bookmarks-{date.today().isoformat()}.html")
    output.write_text(to_netscape_html(nodes), encoding="utf-8")
    if not args.quiet:
        print(f"Wrote {total} bookmarks to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
