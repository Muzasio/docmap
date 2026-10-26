#!/usr/bin/env python3
"""docmap tests.

1. Known answer: scanning tests/fixtures/<name> must give exactly tests/expected/<name>.json
   (that file was reviewed by hand; regenerate it only with --update after reviewing the diff).
2. Self-check must pass on every fixture.
3. Mutation tests: break the facts on purpose; the checker must notice every time.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from check import EFFECTS, check  # noqa: E402
from docmap import build  # noqa: E402
import link  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
EXPECTED = os.path.join(HERE, "expected")


def canonical(facts):
    """Stable, comparable form: everything except time and absolute root."""
    node = lambda n: "|".join(str(n.get(k)) for k in ("id", "kind", "file", "line", "end_line", "parent"))
    edge = lambda e: "|".join(str(e.get(k)) for k in ("from", "to", "kind", "certainty", "file", "line", "term", "via",
                                                       "callback_of", "kw", "delay")) \
        + ("|" + " ".join(e["args"]) if "args" in e else "")
    unk = lambda u: "%s|%s|%s" % (u["file"], u["line"], u["reason"])
    return {"nodes": sorted(set(map(node, facts["nodes"]))), "edges": sorted(set(map(edge, facts["edges"]))),
            "unknown": sorted(set(map(unk, facts["unknown"]))),
            "ambiguous": sorted({"%s|%s|%d" % (a["text"], a["file"], a["line"]) for a in facts["ambiguous"]}),
            "link_errors": sorted({"%s|%d" % (e["file"], e["line"]) for e in facts["link_errors"]})}


# Programs installed on the PC where the known answers were made. A doc term like `nft` is "ambiguous" when it
# is also an installed program, so the test fakes this list: same result on any PC.
INSTALLED_WHEN_MADE = {"nft"}


def known_answer(name, update):
    real_which = link.shutil.which
    link.shutil.which = lambda cmd: "/usr/bin/" + cmd if cmd in INSTALLED_WHEN_MADE else None
    try:
        facts = build(os.path.join(FIXTURES, name), ignore=["profiles"])
    finally:
        link.shutil.which = real_which
    got, path = canonical(facts), os.path.join(EXPECTED, name + ".json")
    if update:
        with open(path, "w") as f:
            json.dump(got, f, indent=1)
        print("UPDATED", path)
        return facts, True
    with open(path) as f:
        want = json.load(f)
    ok = True
    for key in want:
        missing, extra = set(want[key]) - set(got[key]), set(got[key]) - set(want[key])
        for x in sorted(missing):
            print("  MISSING %s: %s" % (key, x))
        for x in sorted(extra):
            print("  EXTRA   %s: %s" % (key, x))
        ok = ok and not missing and not extra
    print("%s known answer (%s): %s" % ("PASS" if ok else "FAIL", name, {k: len(v) for k, v in got.items()}))
    return facts, ok


def mutations(facts, root):
    """Each mutation breaks one fact; check() must report a problem for each."""
    def first(kind, pred=lambda x: True, items="edges"):
        return next(i for i, x in enumerate(facts[items]) if x["kind"] == kind and pred(x))

    cases = []
    f = copy.deepcopy(facts)
    del f["edges"][first("calls", lambda e: e["to"].startswith("py:") and e["kind"] == "calls")]
    cases.append(("drop one internal call", f))
    f = copy.deepcopy(facts)
    f["nodes"][first("method", items="nodes")]["line"] += 1
    cases.append(("move a method to the wrong line", f))
    f = copy.deepcopy(facts)
    f["nodes"][first("heading", items="nodes")]["line"] += 1
    cases.append(("move a heading to the wrong line", f))
    f = copy.deepcopy(facts)
    f["edges"].append(dict(f["edges"][0], to="py:nowhere"))
    cases.append(("link to a node that does not exist", f))
    f = copy.deepcopy(facts)
    f["nodes"].append(dict(f["nodes"][first("function", items="nodes")], id="py:fake:ghost", name="ghost"))
    cases.append(("invent a function", f))
    f = copy.deepcopy(facts)
    f["link_errors"].append({"file": "docs/README.md", "line": 1, "problem": "planted"})
    cases.append(("broken doc link", f))
    ok = True
    for label, mutated in cases:
        caught = bool(check(mutated, root))
        ok = ok and caught
        print("  %s mutation: %s" % ("caught " if caught else "MISSED ", label))
    print("%s mutation tests" % ("PASS" if ok else "FAIL"))
    return ok


def stale_test(facts):
    """Hand edits pointing at missing things must be reported; valid ones must not."""
    from check import stale_edits
    real = next(n["id"] for n in facts["nodes"] if n["kind"] == "method")
    layout = {"positions": {"calls": {real: [1, 2], "py:gone:a": [3, 4]}},
              "groups": {"calls": [{"name": "g", "members": [real, "py:gone:b"]}]},
              "labels": {real: "ok", "py:gone:c": "x"}, "notes": {"py:gone:d": "x"},
              "links": [{"from": real, "to": "py:gone:e"}, {"from": real, "to": real}]}
    got = sorted(s["id"] for s in stale_edits(layout, facts))
    ok = got == ["py:gone:a", "py:gone:b", "py:gone:c", "py:gone:d", "py:gone:e"]
    print("%s stale-edit test (%s)" % ("PASS" if ok else "FAIL", got))
    return ok


SKIPPED = []


def fix_tests():
    """Bugs found in review (2026-10-14). Each check fails on the old code."""
    import io
    import shutil
    import tempfile
    import threading
    import time
    import types
    import render
    import lookup
    from check import ConfigError
    from scan.docs_scan import scan_markdown
    fails = []

    def expect(name, ok):
        if not ok:
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="docmap-test-")
    try:
        # 1. Tables: "\|" is a "|" inside a cell (GitHub rule), also inside `code`.
        expect("table cells", render.table_cells(r"| `a\|b` | c |") == ["`a|b`", "c"])
        expect("table plain", render.table_cells("|x|y|") == ["x", "y"])
        os.makedirs(os.path.join(tmp, "p", "docs"))
        with open(os.path.join(tmp, "p", "docs", "t.md"), "w") as f:
            f.write("| A | B |\n|---|---|\n| `a\\|b` | c |\n")
        terms = scan_markdown(os.path.join(tmp, "p"), "docs/t.md")[2]
        expect("table term", [t["text"] for t in terms] == ["a|b"])
        with open(os.path.join(tmp, "p", "docs", "t.md")) as f:
            page = render.markdown(f.read(), "docs/t.md",
                                   render.Linker({"edges": [], "ambiguous": [], "nodes": []}), False)
        expect("table html", "<td><code>a|b</code></td><td>c</td>" in page)

        # 2. Images next to the docs load from the project; anything outside it never does.
        expect("image local", render.image_src("img/a b.png", "docs/x.md") == "docmap://project/docs/img/a%20b.png")
        expect("image up", render.image_src("../shot.png", "docs/x.md") == "docmap://project/shot.png")
        for bad in ("../../etc/x.png", "/etc/x.png", "javascript:alert(1)", "file:///etc/x.png"):
            expect("image blocked " + bad, render.image_src(bad, "docs/x.md") is None)
        expect("image web", render.image_src("https://e.org/a.png", "docs/x.md") == "https://e.org/a.png")

        # 3. A broken docmap.json gives a clear error, not a traceback.
        os.makedirs(os.path.join(tmp, "p", "docs", "viewer"))
        cfg = os.path.join(tmp, "p", "docs", "viewer", "docmap.json")
        for text in ("{bad", '["x"]', '{"ignore": "x"}'):
            with open(cfg, "w") as f:
                f.write(text)
            try:
                build(os.path.join(tmp, "p"))
                expect("config error " + text, False)
            except ConfigError:
                pass
        with open(cfg, "w") as f:
            f.write('{"ignore": ["x"]}')
        expect("config ok", build(os.path.join(tmp, "p"))["doc_files"] == ["docs/t.md"])

        # 4. Lookups on several threads must not lose each other's counts.
        class Answer(io.BytesIO):
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def slow_answer(req, timeout=None):
            time.sleep(0.02)
            return Answer(b'{"items": []}')

        real, lookup.urllib.request.urlopen = lookup.urllib.request.urlopen, slow_answer
        try:
            lk = lookup.Lookup(os.path.join(tmp, "out"))
            threads = [threading.Thread(target=lk._get, args=("wikipedia", "https://x/%d" % i)) for i in range(6)]
            [t.start() for t in threads]
            [t.join() for t in threads]
            expect("lookup counts", len(lk._state()["calls"]["wikipedia"]) == 6)
        finally:
            lookup.urllib.request.urlopen = real

        # 5. Window: files only inside the project (symbolic links followed), error text escaped.
        try:
            import viewer
        except Exception as e:  # no WebKitGTK here: the rest still ran
            SKIPPED.append("window file checks (%s)" % e.__class__.__name__)
        else:
            root = os.path.join(tmp, "p")
            with open(os.path.join(tmp, "secret.txt"), "w") as f:
                f.write("x")
            with open(os.path.join(root, "ok.txt"), "w") as f:
                f.write("x")
            os.symlink(os.path.join(tmp, "secret.txt"), os.path.join(root, "link.txt"))
            fake = types.SimpleNamespace(project={"root": root})
            fake.safe_path = lambda rel: viewer.Viewer.safe_path(fake, rel)
            expect("path inside", fake.safe_path("ok.txt") is not None)
            expect("path symlink out", fake.safe_path("link.txt") is None)
            expect("path ../", fake.safe_path("../secret.txt") is None)
            expect("error escaped", "<b>" not in viewer.Viewer.render_file(fake, "<b>x</b>"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s review fixes%s" % ("FAIL" if fails else "PASS", "".join("\n  - " + f for f in fails)))
    return not fails


def hand_test(name):
    """Compare the scanner with an answer written by hand (tests/expected_hand/<name>.json)."""
    with open(os.path.join(HERE, "expected_hand", name + ".json")) as f:
        want = json.load(f)
    facts = build(os.path.join(FIXTURES, name))
    if facts["skipped"]:  # Rust/C/C++/C# files, and the parsers do not work on this Python
        print("SKIP hand-written answer (%s): tree-sitter parsers not installed for Python %d.%d" % (
            (name,) + tuple(sys.version_info[:2])))
        SKIPPED.append(name)
        return True
    by_id = {n["id"]: n for n in facts["nodes"]}
    short = lambda i: i.split(":", 2)[2].split("@")[0] if i.startswith(("ts:", "py:")) and i.count(":") >= 2 else i  # noqa: E731
    got = {
        "defs": ["%s|%s|%d|%s" % (n["kind"], n["file"], n["line"], short(n["id"])) for n in facts["nodes"]
                 if n["id"].startswith(("ts:", "py:")) and n["kind"] in ("function", "method", "class", "namespace", "constant")],
        "calls": ["%s|%s|%s|%d" % (short(e["from"]), short(e["to"]), e["file"], e["line"]) for e in facts["edges"] if e["kind"] == "calls"],
        "references": ["%s|%s|%s|%d|%s|%s" % (short(e["from"]), short(e["to"]), e["file"], e["line"], e.get("callback_of"),
                                                e.get("delay")) for e in facts["edges"] if e["kind"] == "references"],
        "instantiates": ["%s|%s|%s|%d" % (short(e["from"]), short(e["to"]), e["file"], e["line"]) for e in facts["edges"] if e["kind"] == "instantiates"],
        "imports": ["%s|%s|%d" % (e["file"], by_id[e["to"]]["name"], e["line"]) for e in facts["edges"] if e["kind"] == "imports"],
        "includes": ["%s|%s|%d" % (e["file"], by_id[e["to"]]["name"], e["line"]) for e in facts["edges"] if e["kind"] == "includes"],
        "effects": ["%s|%s|%s|%s|%d|%s" % (short(e["from"]), e["kind"], by_id[e["to"]]["name"], e["file"], e["line"],
                                           " ".join(e.get("args", []))) for e in facts["edges"] if e["kind"] in EFFECTS
                    and e["file"] in facts["ts_files"]],
        "via": ["%s|%s|%s|%d|%s" % (short(e["from"]), e["kind"], by_id[e["to"]]["name"], e["line"], e["via"])
                for e in facts["edges"] if e.get("via") and e["file"] in facts["ts_files"]],
        "unknown_lines": ["%s|%d" % (u["file"], u["line"]) for u in facts["unknown"]],
        "build_dirs": facts["build_dirs"],
    }
    ok = True
    for key in got:
        w, g = set(want.get(key, [])), set(got[key])
        for x in sorted(w - g):
            print("  MISSING %s: %s" % (key, x))
        for x in sorted(g - w):
            print("  EXTRA   %s: %s" % (key, x))
        ok = ok and w == g
    if name.startswith(("io_", "vars_")):  # mutation: move a file/command link to the next line; the checker must notice
        victim = next(e for e in facts["edges"] if e["kind"] in EFFECTS and e["file"] in facts["ts_files"])
        moved = dict(victim, line=victim["line"] + 1, end_line=victim.get("end_line", victim["line"]) + 1)
        caught = bool(check(dict(facts, edges=[moved if e is victim else e for e in facts["edges"]]), facts["root"]))
        print("  %s mutation: move %s %s to the next line" % ("caught " if caught else "MISSED ", victim["kind"], victim["to"]))
        ok = ok and caught
    victim = next((e for e in facts["edges"] if "value_line" in e), None)
    if victim is not None:  # mutation: point a variable's string to the wrong line; the checker must notice
        moved = dict(victim, value_line=victim["value_line"] + 1)
        caught = bool(check(dict(facts, edges=[moved if e is victim else e for e in facts["edges"]]), facts["root"]))
        print("  %s mutation: move the string of %s to the wrong line" % ("caught " if caught else "MISSED ", victim["to"]))
        ok = ok and caught
    # mutation: drop one definition the text pattern can see; the checker must notice
    kinds = {"rust": ("function", "method"), "pynested": ("function", "method"),
             "io_rust": ("function",), "vars_rust": ("function",), "pyclasses": ("function", "method")}.get(name, ("class",))
    victim = next((n for n in facts["nodes"] if n["id"].startswith(("ts:", "py:")) and n["kind"] in kinds), None)
    if victim is not None or not name.startswith(("io_", "vars_")):  # io_c, io_cpp have no class for the text pattern
        mutated = dict(facts, nodes=[n for n in facts["nodes"] if n is not victim])
        caught = bool(check(mutated, facts["root"]))
        print("  %s mutation: drop %s" % ("caught " if caught else "MISSED ", victim and victim["id"]))
        ok = ok and caught
    print("%s hand-written answer (%s)%s" % ("PASS" if ok and not facts["problems"] else "FAIL", name,
                                              "".join("\n  - " + p for p in facts["problems"])))
    return ok and not facts["problems"]


def main():
    update = "--update" in sys.argv
    results = []
    hand = {n[:-5] for n in os.listdir(os.path.join(HERE, "expected_hand"))} if not update else set()
    for name in sorted(hand):
        results.append(hand_test(name))
    for name in sorted(n for n in os.listdir(FIXTURES) if n not in hand and os.path.exists(os.path.join(EXPECTED, n + ".json")) or update and n == "flatnet"):
        facts, ok = known_answer(name, update)
        problems = facts["problems"]
        print("%s self-check (%s)%s" % ("PASS" if not problems else "FAIL", name,
                                         "".join("\n  - " + p for p in problems)))
        results += [ok, not problems, mutations(facts, facts["root"]), stale_test(facts)]
    if not update:
        results.append(fix_tests())
    note = " (%d skipped: %s)" % (len(SKIPPED), ", ".join(SKIPPED)) if SKIPPED else ""
    print(("ALL PASS" if all(results) else "SOME TESTS FAILED") + note)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
