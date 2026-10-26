# FlatNet documentation

FlatNet is a small desktop program for Linux. It does two jobs for **Flatpak** apps:

1. **Internet control per app.** You can make a running Flatpak app Online, LAN only (home network only) or Cut (no network), with one click and without restarting it.
2. **Throwaway profiles.** You can open Chrome, Firefox, Falkon or LibreOffice with a fresh, separate profile. The profile is deleted automatically when the app closes, unless you click **Keep (save)**.

It is one Python file with a Tkinter window. Admin (root) rights are used only for firewall changes, through a password prompt.

## Where to start

| You want to... | Read |
|---|---|
| Know what each file is | [Folder and file structure](#folder-and-file-structure) below |
| Use the program | [USER-GUIDE.md](USER-GUIDE.md) |
| Install it on another Linux PC | [SETUP.md](SETUP.md) |
| Fix a problem | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

## Folder and file structure

```
flatnet/
├── flatnet.py          the whole program (406 lines)
├── apps.json           list of apps that can get throwaway profiles
├── profiles/           all profiles (temp and kept) live here
│   └── <App>/<name>/   one folder per profile, for example profiles/Chrome/temp-k3j9x1ab/
│       ├── profile.json   that profile's settings: {"mode": "...", "saved": true/false}
│       └── data/          everything the app writes (cookies, history, cache, settings)
├── state.json          created by the program: which apps/profiles are blocked right now
├── defaults.json       created by the program: default network mode per app
├── .lock               created by the program: stops a second FlatNet window from opening
└── docs/               this documentation
    ├── README.md            this file
    ├── USER-GUIDE.md        how to use every button
    ├── SETUP.md             install on a new Linux distro
    └── TROUBLESHOOTING.md   known errors, limits and fixes
```

One file lives outside the folder:

```
~/.local/share/applications/flatnet.desktop    the "FlatNet" entry in your app menu
```

## Guide to each file

### `flatnet.py`
The program. Start it with `python3 flatnet.py` or from the app menu. Main parts, in order:

| Part | What it does |
|---|---|
| Settings at the top (`HERE`, `PROFILES`, `STATE`, `DEFAULTS`, `RUNTIME`) | File paths. Everything is relative to the folder the program is in, so you can move the folder. |
| `MODES` | The four network modes: `online`, `lan`, `cut`, `offline`. |
| `SCOPE_RE`, `SAFE_PATH` | Patterns used to recognise Flatpak processes and to reject unsafe text before it reaches the firewall. |
| `LAN_ONLY` | The address ranges counted as "home network". |
| `HELPER` | A tiny Python script that runs as root and applies firewall rules. It is started once per session with `pkexec`. |
| `scan()` | Finds every running Flatpak app by reading `/proc`. |
| `load_profiles()`, `save_meta()` | Read and write the profiles in `profiles/`. |
| `FlatNet` class | The window, buttons and all actions. |
| `apply()` | Rebuilds the firewall table `inet flatnet` from the current blocks. |
| `tick()` | Runs every 0.2 seconds: finds newly started apps and blocks them at once if they should be blocked. Redraws the window every 2 seconds. |
| Bottom (`__main__`) | Makes sure only one FlatNet window is open, then starts it. |

### `apps.json`
The apps that can get throwaway profiles. Current content:

```json
{
  "Chrome":      {"id": "com.google.Chrome",           "args": ["--no-first-run", "--no-default-browser-check"]},
  "Firefox":     {"id": "org.mozilla.firefox",         "args": ["--no-remote"]},
  "Falkon":      {"id": "org.kde.falkon",              "args": ["--no-remote"]},
  "LibreOffice": {"id": "org.libreoffice.LibreOffice", "args": ["-env:UserInstallation={url}/lo"]}
}
```

| Key | Meaning |
|---|---|
| name (`"Chrome"`) | Name shown in the window. Also the folder name under `profiles/`. |
| `id` | The Flatpak app ID (see `flatpak list --app`). |
| `args` | Extra start options. `{dir}` becomes the profile's `data` folder path, and `{url}` becomes the same path as a `file://` address. |
| `command` (optional) | The program to run inside the Flatpak. If missing, FlatNet reads it from `flatpak info -m <id>`. |

How to add an app: see [USER-GUIDE.md, "Add another app"](USER-GUIDE.md#add-another-app-for-profiles).

### `profiles/`
Every profile is a folder `profiles/<App>/<name>/`:
- `profile.json` stores `mode` (the network mode used at launch) and `saved` (`true` = kept, `false` = temp).
- `data/` holds everything the app writes. The app is told to use `data/config`, `data/data`, `data/cache` and `data/state` instead of its normal folders. LibreOffice also uses `data/lo`.

Temp profile folders are named `temp-` plus random characters and can only be opened by your user account (permission `700`).

### `state.json`
Written after each successful firewall change. It stores which groups are blocked, for example:

```json
{"app:com.discordapp.Discord": "cut", "/home/you/.../profiles/Falkon/work": "lan"}
```

A group is either `app:<flatpak id>` (a normal app) or the folder path of a profile. When FlatNet starts and this file lists blocks, it asks for the password and re-applies them.

### `defaults.json`
Written when you change a default in the "Default network per app" box, for example `{"Chrome": "lan"}`. Apps not listed default to `online`.

### `.lock`
Empty file. While FlatNet is open it holds a lock on this file. A second FlatNet then shows "FlatNet is already open." The lock is released when the program closes, even if the file stays.

### Firewall table (not a file)
FlatNet's rules live in the kernel's firewall as the nftables table `inet flatnet`, with two chains:
- `out` (hook `output`): blocking rules and "Sent" counters
- `inn` (hook `input`): "Received" counters

See them with `sudo nft list table inet flatnet`.
