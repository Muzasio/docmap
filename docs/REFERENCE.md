# docmap reference

Every command, setting, file and limit. For a short introduction see the [README](../README.md); to learn how to read the diagrams see the [user guide](USER-GUIDE.md).

## Start

| What | Command |
|---|---|
| Open the window for a project | `python3 docmap.py view <project folder>` |
| Open it from a copy inside a project's `docs/viewer/docmap/` | `python3 docs/viewer/docmap/docmap.py view` |
| Only scan and write the report (no window) | `python3 docmap.py scan <project folder> --ignore <folders>` |
| Check what is installed, and how to install what is missing | `python3 docmap.py setup` |
| Install a missing part (asks first) | `python3 docmap.py setup --install <part>` (part: `window`, `fallback` or `parsers`) |
| Show the install command only | `python3 docmap.py setup --install window --dry-run` |
| Run all tests | `python3 tests/run_tests.py` |
| Short `docmap` command (once, from the docmap folder) | `ln -s "$PWD/bin/docmap" ~/.local/bin/docmap`, then `docmap` opens the current folder |

Folders to skip can also go in `<project>/docs/viewer/docmap.json`: `{"ignore": ["profiles"]}`. Always skipped: `.git`, `__pycache__`, `.venv`, `venv`, `node_modules`, `.mypy_cache`, `.pytest_cache`, and `docs/viewer` itself.

## What it reads

| Language | Parser | Needs |
|---|---|---|
| Python | Python's own `ast` | nothing extra |
| Rust, C, C++, C# | tree-sitter | `python3 docmap.py setup --install parsers` (goes into `docmap/.deps/py3.X`, one folder per Python version, no password) |
| Markdown docs | docmap's own reader | nothing extra |

A `.h` file is read as C++ when the project has C++ files, otherwise as C. If tree-sitter is missing, those files are listed under "Files NOT read" in the coverage report.

## How accuracy is kept

1. **Three levels**, drawn differently:
   - solid line = **certain**: written directly in the code (a definition, an import, `self.apply()` in Python)
   - dashed line = **proven indirectly**: one simple, checkable step (a callback like `command=self.keep`, a wrapper function, `App::new()` with `App` defined once in the project)
   - **not understood**: listed in the Coverage view with file and line, **never drawn**
2. **Every fact points to a real line.** The self-check opens the file and confirms the line holds that name.
3. **Two independent methods must agree:**
   - Python: the parser, and a separate text search (comments and strings blanked by Python's tokenizer), both find definitions and calls.
   - Rust: the parser and a text pattern both find `fn` names. C, C++, C#: both find type names.
   - Rust, C, C++, C# files and commands: the library name must be on that line, and the path or command must be written inside the call (or, for a variable or constant, the variable's name must be in the call and the string on the line where it is set).
   - Comments, strings and characters are blanked in one left-to-right pass, so `"a//b"` or `'"'` cannot fool the text pattern.
   - Any difference is shown as a red "Self-check FAILED" badge.
4. **Doc terms link only on exact matches.** `apply()` or `FlatNet.apply` links; a bare name that is also a command run by the project, a program installed on this PC, or a Python built-in (like `nft`) is listed as ambiguous instead.
5. **Your edits never change facts.** They live in `layout.json`; edits that point at removed code are shown as stale.
6. **Tests:** a frozen FlatNet copy, hand-written answers for Rust, C, C++, C# (code; files and commands; variables, constants and wrapper functions; shapes that broke on real projects) and Python (nested functions, nested classes), mutation tests (the checker must catch planted mistakes), and a stale-edit test. Each hand-written answer was written before the scanner was first run on it.

## The window

| Part | What it does |
|---|---|
| Views | **Overview** (modules, types, libraries, commands, files), **Functions & calls**, **Files & commands**, **Docs** (which doc explains which code), **Runtime** (callbacks: timers, buttons, threads; a loop on a box means it re-schedules itself), **Coverage** (self-check, stale edits, everything not understood) |
| Click a box | Highlights its links, shows details (location, docs that explain it, what it uses, what uses it), opens the file at the line |
| Tabs (right) | One per file, with line numbers. Code lines show call chips (`→ apply`); doc terms are underlined (solid = certain, dashed = indirect, dotted orange = ambiguous, not linked) |
| Open in default app | Opens the current tab's file in your normal editor |
| Search | Finds boxes by name |
| Rescan | Reads the project again |
| Edit layout | Drag boxes (Shift+click for several), Group, Rename label (the real name stays visible), Note, Link to... (your own links, purple), Reset positions, Undo (Ctrl+Z). Saved in `docs/viewer/layout.json` |
| Internet switch | Off by default. Off: the page can load only local files, and the web engine's network goes to a dead proxy (tested: loading a web page fails). On: web links open in a separate window, and **Look up online** works |
| Look up online | In the details panel, with Internet on. Searches Wikipedia, Stack Overflow, GitHub, Microsoft Learn, and gives links to Python, Rust and C++ docs search pages. Tick results and **Save selected**: saved into `docs/viewer/research/` with link, date and license, shown as "external" |

If WebKitGTK is missing, docmap opens a simpler **Tkinter window** with the same views, details, tabs, line numbers and clickable links (read-only: no editing, no lookup), plus an "Install the full window..." button.

## Files

```
docmap/
├── docmap.py         start here: scan / view / setup commands
├── scan/
│   ├── python_scan.py  Python facts (ast)
│   ├── ts_scan.py      Rust, C, C++, C# facts (tree-sitter)
│   ├── ts_effects.py   list of known library calls that touch files or run commands (Rust, C, C++, C#)
│   └── docs_scan.py    Markdown headings, `terms`, links
├── link.py           joins doc terms and links to code (exact matches only)
├── check.py          self-checks, stale edits, coverage report
├── render.py         files to HTML for tabs (line numbers, chips, linked terms)
├── viewer.py         the WebKitGTK window (internet switch, messages from the page)
├── web/              the page: index.html, style.css, app.js (views, layout, editing, lookup panel)
├── fallback.py       the Tkinter window
├── setup_deps.py     what is missing and how to install it
├── lookup.py         online lookup (only used when you ask)
├── bin/docmap        short launcher (finds docmap.py next to itself)
├── tests/            run_tests.py, fixtures/ (test projects), expected/ and expected_hand/ (answers)
├── docs/             USER-GUIDE.md, REFERENCE.md (this file), images/
└── .deps/py3.X/      tree-sitter parsers for that Python version (created by setup --install parsers, not in git)
```

Written into the project's `docs/viewer/`:

| File | Made by | Edit by hand? |
|---|---|---|
| `facts.json` | every scan | no |
| `coverage.md` | every scan | no |
| `layout.json` | Edit layout | through the window |
| `settings.json` | Internet switch | can |
| `docmap.json` | you | yes: `ignore`, and `contact` for the online lookup |
| `research/*.json` | Save selected | can delete |
| `research/.usage.json` | lookup | no (rate limits and 1-hour cache) |

## Limits (by design)

- Calls on variables whose type is not known (`obj.method()`, `app.run()`) are **not drawn**; they are listed under Coverage.
- Rust, C, C++, C#: calls are at most "proven indirectly". Files and commands are found only for the library calls listed in `scan/ts_effects.py` (for example `std::fs::write`, `fopen`, `system`, `std::ifstream`, `File.ReadAllText`, `Process.Start`), and only when the path or command is known for sure: a plain string in the code, a variable set once to a plain string and never changed (not reassigned, not shadowed, not handed out with `&`, `&mut`, `ref` or `out`), a constant (Rust `const`/`static`, C `#define`, a top-level C/C++ name no project file assigns, C# `const`/`readonly`), or a parameter of a wrapper function that is called with one of those (drawn as "via" the wrapper). Not followed: a path built at run time (`dir.join("x")`, `format!`), a C array (`char buf[] = "x"`), a non-const C++ `std::string`, a wrapper of a wrapper, `o.open("x")` on a stream, a call the list does not know. These go to the coverage report.
- C++ `std::ifstream in(path);` looks like a function declaration to the parser. It is counted only when `path` is a known variable or constant.
- Rust `fn` written inside a macro (`proptest! { fn ... }`, `macro_rules!`) is not read; each one is listed in the coverage report.
- Build output is skipped: `target/` next to `Cargo.toml`, `bin/` and `obj/` next to a `.csproj`, and any folder holding `CMakeCache.txt`. The coverage report lists them.
- Shell lines like `system("ls | wc -l")`: only the first program (`ls`) is drawn; the line is also listed in the coverage report.
- Python: calls on instance attributes (`self.helper.stdin.write`) are not drawn.
- Online sources: GitHub allows 10 searches per minute without login; Stack Exchange 300 requests per day per IP address; the same search is answered from a 1-hour local cache. Wikimedia asks for contact details in the User-Agent: set `"contact"` in `docs/viewer/docmap.json` (for example a website or email). Until then docmap sends "contact not set".

## Troubleshooting

| Problem | Fix |
|---|---|
| Window crashes with `Error 71 (Protocol error) dispatching to Wayland display` | docmap already sets `WEBKIT_DISABLE_DMABUF_RENDERER=1`. If you set `DOCMAP_DMABUF=1`, remove it. |
| "Simple view" opens instead of the full window | WebKitGTK or PyGObject is missing: `python3 docmap.py setup --install window` |
| Rust/C/C++/C# files listed as NOT read | `python3 docmap.py setup --install parsers` |
| Red "Self-check FAILED" | Open Coverage: each line names the file and line where the two methods disagree. The diagram may be wrong there. |
| Red "N stale edit(s)" | Your edit points at renamed or removed code. Coverage lists them with **Remove** buttons. |
| "Look up online" is greyed out | Turn the Internet switch on. |
| Lookup says "limit reached" or "asked us to wait" | A rate limit; wait and try again. |
| `docmap: docs/viewer/docmap.json cannot be read` (or Rescan says so) | The file is not valid JSON. It must look like `{"ignore": ["folder"]}`. Fix it or delete it. |
| An image in a doc shows "image not shown: outside the project" | Images load only from inside the project (or from the web with Internet on). Move the image into the project. |
| Debug the page | Start with `DOCMAP_DEBUG=1` to allow the web inspector. |

Tested on CachyOS (Arch based), Python 3.14.7, WebKitGTK 2.52 (API 4.1), Tk 8.6, tree-sitter 0.26.0. Other distros: install commands are the usual package names, not tested.

Older Python (all tests, 2026-10-14):

| Python | Python + docs scanning, checks | Rust/C/C++/C# parsers | Window |
|---|---|---|---|
| 3.14.7 | pass | pass | tested by hand earlier |
| 3.10.20 (uv) | pass | pass (tree-sitter 0.26 installed into `.deps/py3.10`) | not tested |
| 3.8.20 (uv) | pass | cannot install: needs tree-sitter 0.22+, which needs Python 3.9+ (pip says so) | not tested |
| 3.7.17, 3.6.15 (podman `python:X-slim`) | pass | not tried (same reason) | not tested (no Tk/GTK in the container) |

Python 3.9 is not tested. On Python before 3.8, end lines of functions come from Python's tokenizer instead of the parser (3.8+ gives them directly).
