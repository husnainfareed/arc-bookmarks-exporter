# arc-bookmarks-exporter

Get your tabs out of Arc Browser. This turns Arc's sidebar (pinned tabs, folders, and optionally unpinned tabs) into a standard bookmarks HTML file that Chrome, Firefox, Safari, Edge, Brave, or Zen can import.

It's a single Python file with no dependencies. Works on macOS and Windows.

## Usage

```bash
python3 arc_export.py              # pinned tabs → arc-bookmarks-YYYY-MM-DD.html
python3 arc_export.py --unpinned   # include unpinned tabs too
python3 arc_export.py --dry-run    # show counts per space, write nothing
```

| Option | |
| --- | --- |
| `-o, --output PATH` | where to write the HTML file |
| `-i, --input PATH` | use a specific `StorableSidebar.json` instead of Arc's own |
| `--unpinned` | also export unpinned tabs (each space gets a separate "(unpinned)" folder) |
| `--dry-run` | print what would be exported and stop |
| `-q, --quiet` | print errors only |

Each Arc space becomes a folder, and folders inside a space keep their nesting. If you use more than one Arc profile, each profile gets its own top-level folder.

## Where Arc keeps its data

- **macOS:** `~/Library/Application Support/Arc/StorableSidebar.json`
- **Windows:** `%LOCALAPPDATA%\Packages\TheBrowserCompany.Arc*\LocalCache\Local\Arc\StorableSidebar.json`

The script only reads this file, so nothing in Arc changes.

## Importing

In the other browser, look for **Import bookmarks** (it's often under *Bookmarks → Import* or in settings) and choose the generated `.html` file.

## License

MIT
