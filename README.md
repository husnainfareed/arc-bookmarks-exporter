# arc-bookmarks-exporter

Leaving Arc, or just want a backup? Arc has no proper bookmarks export: your pinned tabs and folders live in its sidebar, not in a bookmarks file. This script reads that sidebar and writes a regular bookmarks HTML file that any browser can import.

```bash
python3 arc_export.py
# Personal: 163
# Work: 132
# Wrote 295 bookmarks to arc-bookmarks-2026-10-23.html
```

## Features

- ✅ **Every Profile**: Exports from all your Arc profiles at once
- ✅ **Pinned & Unpinned**: Pinned tabs by default, unpinned ones with `--unpinned`
- ✅ **Folder Structure Kept**: Spaces and nested folders come out just as they are in Arc
- ✅ **Sidebar Order**: Tabs stay in the same order as your sidebar
- ✅ **Universal Format**: Standard bookmarks HTML that every major browser imports
- ✅ **macOS & Windows**: Finds Arc's data automatically on both
- ✅ **Robust Parsing**: Handles missing titles, empty folders and odd characters
- ✅ **Verbose & Dry Run**: See what was found and skipped before writing anything
- ✅ **Read-Only**: Never modifies Arc's data

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

## Seeing what it does

Add `-v` to see which file it read, what it found, and what it skipped:

```
$ python3 arc_export.py -v
reading /Users/you/Library/Application Support/Arc/StorableSidebar.json
1 profile, 3 spaces
Personal: 163
Work: 132
Side projects: 41
skipped: 17 unpinned tabs (use --unpinned), 2 tabs with no URL, 1 empty folder
Wrote 336 bookmarks to arc-bookmarks-2026-10-23.html
```

With more than one profile, spaces are listed under each profile:

```
2 profiles, 4 spaces
Profile 1: 336
  Personal: 163
  Work: 132
  Side projects: 41
Profile 2: 58
  School: 58
```

All of this goes to the terminal, never into the exported file. Combine `-v` with `--dry-run` to check everything before writing anything.

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

**`error: can't read ...` or `error: ... is not a text file`**
The file exists but couldn't be opened. Check its permissions, or make sure `--input` points at `StorableSidebar.json` itself and not some other file.

**`error: ... is not valid JSON`**
The file is damaged or only partly written. Quit Arc so it saves the file properly, then try again.

**`error: can't write ...`**
The folder you gave to `-o` doesn't exist, or you can't write to it. Pick another path or create the folder first.

**`error: no bookmarks found (try --unpinned)`**
None of your spaces have pinned tabs. If all your tabs are unpinned, run it again with `--unpinned`.

**Some tabs are missing**
Run with `-v` to see what was left out (see [Seeing what it does](#seeing-what-it-does)).

Unpinned tabs are skipped unless you pass `--unpinned`. Tabs that have no URL, and folders with nothing in them, are always left out.

**Arc changed something and it broke**
Arc's file format isn't documented, so an update can change it. Please [open an issue](https://github.com/husnainfareed/arc-bookmarks-exporter/issues) with your OS, your Python version, and the output of `python3 arc_export.py -v --dry-run`.

## Contributing

Issues and pull requests are welcome. The whole tool is `arc_export.py`, about 200 lines, so it's easy to find your way around.

## License

[MIT](LICENSE)
