# arc-bookmarks-exporter

Leaving Arc, or just want a backup? Arc has no proper bookmarks export: your pinned tabs and folders live in its sidebar, not in a bookmarks file. This script reads that sidebar and writes a regular bookmarks HTML file that any browser can import.

```bash
python3 arc_export.py
# MY SPACE: 163
# WORK: 132
# Wrote 295 bookmarks to arc-bookmarks-2026-10-23.html
```

## Why use it

- **Your sidebar comes through as you left it.** Each space becomes a folder, nested folders stay nested, and tabs keep the order you see in Arc.
- **Pinned tabs by default.** Add `--unpinned` to bring the loose tabs along too.
- **Every profile.** If you use more than one Arc profile, each one gets its own top-level folder.
- **Imports anywhere.** The output is the standard Netscape bookmarks format that Chrome, Firefox, Safari, Edge, Brave, Zen and others all read.
- **Nothing to install.** It's one Python file that uses only the standard library.
- **Read-only.** It never writes to Arc's data, so it's safe to run while Arc is open.

## Getting started

You need Python 3.8+ (it comes with macOS) and Arc installed on macOS or Windows.

```bash
git clone https://github.com/husnainfareed/arc-bookmarks-exporter.git
cd arc-bookmarks-exporter
python3 arc_export.py --dry-run   # see what it finds first
python3 arc_export.py             # write the file
```

## Options

| Flag | What it does |
| --- | --- |
| `-o, --output PATH` | Write the file to `PATH` instead of `arc-bookmarks-YYYY-MM-DD.html` |
| `--unpinned` | Also export unpinned tabs. They go in a separate "*Space* (unpinned)" folder |
| `--dry-run` | Print the number of bookmarks per space, and write nothing |
| `-i, --input PATH` | Read a specific `StorableSidebar.json`, e.g. one copied from another machine |
| `-v, --verbose` | Also show which file was read, and what was skipped and why |
| `-q, --quiet` | Only print errors |

Some common combinations:

```bash
python3 arc_export.py --unpinned -o ~/Desktop/arc.html   # everything, onto the Desktop
python3 arc_export.py -i ~/Downloads/StorableSidebar.json  # export someone else's sidebar
```

## What you get

```
Bookmarks
├── Personal
│   ├── Daily
│   │   ├── Gmail
│   │   └── Calendar
│   └── Reading list
├── Personal (unpinned)        ← only with --unpinned
└── Work
    └── ...
```

## Importing into another browser

| Browser | Steps |
| --- | --- |
| **Chrome** | Open `chrome://bookmarks`, then ⋮ → *Import bookmarks* |
| **Brave** | Open `brave://settings/importData`, then pick *Bookmarks HTML file* |
| **Edge** | Open `edge://favorites`, then ⋯ → *Import favorites* → *Favorites or bookmarks HTML file* |
| **Firefox / Zen** | Bookmarks → *Manage bookmarks*, then *Import and Backup* → *Import Bookmarks from HTML* |
| **Safari** | File → *Import From* → *Bookmarks HTML File* |

## Where Arc keeps the data

Arc saves the whole sidebar in a single JSON file:

- **macOS:** `~/Library/Application Support/Arc/StorableSidebar.json`
- **Windows:** `%LOCALAPPDATA%\Packages\TheBrowserCompany.Arc*\LocalCache\Local\Arc\StorableSidebar.json`

Inside, every tab and folder is an item that points to its parent. Each space records which item holds its pinned tabs and which holds its unpinned ones. The script groups the items by parent, walks down from each space, and writes out the tree.

## Troubleshooting

**`error: can't find .../StorableSidebar.json`**
Arc isn't installed in the usual place, or it hasn't been opened yet. Find the file yourself and pass it with `--input`.

**`error: no bookmarks found (try --unpinned)`**
None of your spaces have pinned tabs. If all your tabs are unpinned, run it again with `--unpinned`.

**Some tabs are missing**
Run with `-v` to see what was left out:

```
skipped: 16 unpinned tabs (use --unpinned), 2 tabs with no URL, 1 empty folder
```

Unpinned tabs are skipped unless you pass `--unpinned`. Tabs that have no URL, and folders with nothing in them, are always left out.

**Arc changed something and it broke**
Arc's file format isn't documented, so an update can change it. Please [open an issue](https://github.com/husnainfareed/arc-bookmarks-exporter/issues) with your OS, your Python version, and the output of `python3 arc_export.py -v --dry-run`.

## Contributing

Issues and pull requests are welcome. The whole tool is `arc_export.py`, about 170 lines, so it's easy to find your way around.

## License

[MIT](LICENSE)
