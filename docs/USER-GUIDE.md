# How to use docmap to understand a project

A beginner's guide. For install, commands and limits, see the [reference](REFERENCE.md).

## Open it

```
cd <project folder>
docmap
```

`docmap` with no folder opens the folder you are in. `docmap <folder>` opens that folder.
(`docmap` is the launcher in `bin/docmap`; set it up once with `ln -s "$PWD/bin/docmap" ~/.local/bin/docmap` from the docmap folder. Without it: `python3 <path to>/docmap.py view <folder>`.)

## 1. How to read the picture

### A box = one piece of the program

- **Big text**: its name, for example `apply`.
- **Small text**: what kind it is and where it starts, for example `method  line 190`.
- **Colored stripe on the left**: the kind again. The legend at the bottom says which color is which (module = a code file, class, function, method, command, file, ...).

### A line with an arrow = "uses"

- `A → B` means **A uses B**: A calls B, reads file B, or runs command B.
- **Solid line**: certain. Written plainly in the code.
- **Dashed line**: proven in one step. For example a function handed to a button, which runs later.
- **Hover over a line** to see what it is and in how many places.

### Left to right = order

- Boxes on the **far left** are starting points: nothing in the project calls them.
- The further right, the more a box gets used by the boxes before it.

### Moving around

| Do | How |
|---|---|
| Zoom | Mouse wheel, or `+` / `−` |
| Move the picture | Drag the empty background |
| See everything again | **Fit** |
| Jump to a name | **Search** box at the top |

## 2. A route through any project (7 steps)

### Step 1: Overview, the big picture

Shows the code files, the outside libraries they import (like `tkinter` or `subprocess`), the commands the program runs, and the files it touches.

Ask: *what does this program depend on, and what does it touch on my computer?*

### Step 2: Click a box, then read the details panel

The panel under the diagram is where most of the learning happens:

- **Where**: file and line. Click it and the code opens on the right, at that line.
- **Explained in docs**: which docs talk about it. Click to read them.
- **Uses**: what it needs.
- **Used by**: who needs it.

Clicking also highlights the neighbours and dims everything else, so you only see what is connected.

### Step 3: Functions & calls, how the program flows

Start on the **left side** (the starting points). Click one, follow its arrows to the right, and read each function's code in the right panel as you go.

### Step 4: Runtime, what happens when

Things that happen later, not straight away: button clicks, timers, threads.

- `command=` means "runs when this button is clicked".
- `after ... ms` means "runs after a timer".
- A **loop on a box** means it re-schedules itself, for example a timer that runs every few seconds.

This is how you learn what each button actually does.

### Step 5: Files & commands, what it changes on your PC

Which functions read or write which files, and run which commands. This matters most for programs that touch your system.

### Step 6: Docs, the explanations

Shows which doc explains which code. In the right panel, underlined words in a doc are clickable and jump to that code:

- **solid underline**: certain link
- **dashed underline**: proven indirectly
- **dotted orange underline**: more than one possible meaning, so not linked (hover to see the choices)

### Step 7: Coverage, what the picture does NOT show

docmap draws only what it can prove. Anything it could not work out is listed here instead, with file and line, for example `obj.method()` where it does not know what `obj` is.

Remember: **the diagram is everything certain, not everything.** Check Coverage before you decide something is not used.

## 3. Make the map your own (Edit layout)

Turn on **Edit layout** while you learn:

- **Drag** boxes into an order that makes sense to you.
- **Shift+click** several boxes, then **Group**, and give it a name like "firewall part" or "window part".
- **Note**: write in your own words what a function does.
- **Rename label**: give a confusing name a clearer one (the real name stays visible).
- **Link to...**: draw your own purple line, for example "these two belong together".
- **Undo** (Ctrl+Z) if you make a mistake.

Your edits never change the code or the facts. They are saved in `docs/viewer/layout.json` and are there next time. Grouping and writing notes is how you actually learn a project.

## 4. Worked example: FlatNet

Open it: `cd` into your FlatNet folder, then run `docmap`.

1. **Overview**: one Python file, `flatnet.py`. It imports `tkinter` (the window), `subprocess` and `json`, and runs `flatpak`, `systemctl` and `pkexec`. So it is a window app that controls Flatpak apps and needs root for something.
2. **Functions & calls**: click the class `FlatNet`, then `__init__`. That is where the window is built. Follow its line to `tick`.
3. `tick` uses `scan_all` (find running apps), `desired` (what the rules should be), `apply` (make it so) and `refresh` (update the window).
4. **Runtime**: `tick` has a loop on it, labelled `repeats: after 200 ms`. It re-schedules itself with a timer, so the whole check repeats on its own. `__init__` points at `new_temp` with `Button command=`: that is what the "new temp" button does. Other buttons (`keep`, `delete`, `launch_sel`, ...) are set up in a way docmap only proves as "referenced", so you find them by clicking `__init__` and reading its **Uses** list.
5. Click `apply`: it uses `nft`, and it writes the file `state.json`. Click `nft`: it runs `pkexec`, which asks for your password once and then runs `nft` (the firewall tool) as root. Now you know where the program changes your firewall.
6. **Coverage**: lines like `self.app_var.get()` are listed as "method call on a value of unknown type". They are not drawn, but they are real code.
7. In **Edit layout**, group `apply`, `nft` and `desired` as "firewall part", and `__init__`, `refresh` and `fill` as "window part". Now the project has two clear halves.

## Short version

1. **Overview**: what it is.
2. **Functions & calls**: start on the left, follow the arrows.
3. **Click each box**: read the code and the docs it links to.
4. **Runtime**: what the buttons and timers do.
5. **Coverage**: what is not drawn.
6. **Group and write notes** as you understand each part.
