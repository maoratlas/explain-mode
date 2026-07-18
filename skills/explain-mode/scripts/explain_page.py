#!/usr/bin/env python3
"""explain-mode page generator (part of the explain-mode skill, v0.2.1).

Takes lesson content and produces a standalone, self-contained HTML page in
.tmp/ at the repo root, then opens it already rendered (editor preview when
configured, otherwise the OS default browser).

Stdlib only. No network. No dependencies.

Modes:
  simple  (default)  content is a small markdown subset; this script builds
                     the whole page, including RTL/LTR isolation.
  rich               content is a raw HTML fragment for <main>; this script
                     supplies the document shell, base CSS, filename, and
                     opening. Inline <script>/<style> in the fragment are
                     passed through untouched.

Markdown subset understood in simple mode:
  # / ## / ###  headings (rendered one level down: h2/h3/h4; --title is h1)
  blank line    paragraph break
  `inline`      isolated LTR <code>
  ``` fences    isolated LTR <pre><code>
  > lines       highlighted callout box
  - lists       unordered list
  1. lists      ordered list
  **bold**      <strong>

Output lines (for the calling agent to relay):
  PAGE <absolute path>      the file that was written
  OPENED editor (cmd) | browser | none
  WARN <message>            non-fatal problems worth surfacing
"""

import argparse
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RTL_LANGS = {"he", "iw", "ar", "fa", "ur", "yi", "ps", "sd", "ug", "dv", "ckb"}

CSS = """\
:root {
  --bg: #faf9f7; --fg: #1f2430; --accent: #2f6fed;
  --code-bg: #eef1f6; --callout-bg: #eaf1ff; --border: #d8dde6;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14161b; --fg: #e8eaf0; --accent: #7aa2ff;
    --code-bg: #1f232c; --callout-bg: #1c2434; --border: #2a2f3a;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 1.25rem; line-height: 1.9; text-align: start;
}
main { max-width: 44rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }
h1 { font-size: 2rem; line-height: 1.4; margin: 0 0 1.5rem; }
h2 { font-size: 1.5rem; margin: 2.2rem 0 0.8rem; }
h3 { font-size: 1.25rem; margin: 1.8rem 0 0.6rem; }
h4 { font-size: 1.1rem; margin: 1.5rem 0 0.5rem; }
p { margin: 0 0 1.1rem; }
ul, ol { padding-inline-start: 1.6rem; margin: 0 0 1.1rem; }
li { margin-bottom: 0.5rem; }
code {
  background: var(--code-bg); border: 1px solid var(--border);
  border-radius: 0.35rem; padding: 0.1rem 0.45rem; font-size: 0.95em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
pre {
  background: var(--code-bg); border: 1px solid var(--border);
  border-radius: 0.6rem; padding: 1rem 1.2rem; overflow-x: auto;
  margin: 0 0 1.3rem;
}
pre code { background: none; border: none; padding: 0; }
pre, code, .ltr { direction: ltr; text-align: left; unicode-bidi: isolate; }
.lesson-badge {
  font-size: 0.8rem; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--accent); opacity: 0.8; margin-bottom: 0.6rem;
}
.callout {
  background: var(--callout-bg);
  border-inline-start: 0.3rem solid var(--accent);
  border-radius: 0.5rem; padding: 1rem 1.2rem; margin: 0 0 1.3rem;
}
.callout p:last-child { margin-bottom: 0; }
"""

PAGE = """\
<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_text}</title>
<style>
{css}</style>
</head>
<body>
<main>
<div class="lesson-badge">explain-mode · lesson</div>
{heading}{body}
</main>
</body>
</html>
"""

PLACEHOLDER = "\x00{}\x00"
PLACEHOLDER_RE = re.compile("\x00(\\d+)\x00")

# A run of Latin text (letters, digits, common path/identifier punctuation,
# single spaces between Latin words). Must not start mid-entity (&amp;),
# mid-placeholder, or mid-run.
LATIN_RUN = re.compile(
    r"(?<![A-Za-z0-9&#\x00])"
    r"([A-Za-z](?:[A-Za-z0-9._/:\-]|\x20(?=[A-Za-z]))*)"
)

# A single token mixing RTL letters (Hebrew/Arabic ranges) with Latin letters
# directly adjacent — the classic "Latin glyph inside an RTL word" glitch.
MIXED_TOKEN = re.compile(
    r"[^\s<>]*(?:[֐-ࣿ][A-Za-z]|[A-Za-z][֐-ࣿ])[^\s<>]*"
)

UL_ITEM = re.compile(r"[-*]\s+")
OL_ITEM = re.compile(r"\d+[.)]\s+")


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except OSError:
        pass
    return Path.cwd()


def page_path(root: Path) -> Path:
    tmp = root / ".tmp"
    tmp.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    path = tmp / f"explain-mode-{stamp}.html"
    n = 2
    while path.exists():
        path = tmp / f"explain-mode-{stamp}-{n}.html"
        n += 1
    return path


def check_gitignore(root: Path) -> None:
    gi = root / ".gitignore"
    try:
        lines = [l.strip() for l in gi.read_text(encoding="utf-8").splitlines()]
    except OSError:
        lines = []
    if not any(l in (".tmp", ".tmp/") for l in lines):
        print("WARN .tmp/ is not in .gitignore — add it so lesson pages never get committed")


def wrap_latin_runs(text: str) -> str:
    """Wrap bare Latin runs in RTL text with a bidi-isolating span.

    Trailing sentence punctuation is left outside the span so it stays with
    the surrounding RTL sentence.
    """
    def repl(m):
        run = m.group(1)
        core = run.rstrip(".:,;-")
        trail = run[len(core):]
        if not core:
            return run
        return f'<span class="ltr">{core}</span>{trail}'
    return LATIN_RUN.sub(repl, text)


def inline(text: str, rtl: bool, store: list) -> str:
    """Escape, convert `inline code` and **bold**, isolate Latin runs."""
    text = html.escape(text)

    def code_repl(m):
        store.append(f"<code>{m.group(1)}</code>")
        return PLACEHOLDER.format(len(store) - 1)

    text = re.sub(r"`([^`\n]+)`", code_repl, text)
    if rtl:
        text = wrap_latin_runs(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def md_to_html(md: str, rtl: bool) -> str:
    """Convert the simple-mode markdown subset to body HTML."""
    store: list = []

    def fence_repl(m):
        store.append(
            "<pre><code>%s</code></pre>" % html.escape(m.group(1).rstrip("\n"))
        )
        return "\n\n" + PLACEHOLDER.format(len(store) - 1) + "\n\n"

    md = re.sub(r"```[^\n]*\n(.*?)```", fence_repl, md, flags=re.S)

    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        if PLACEHOLDER_RE.fullmatch(block):
            out.append(block)
        elif block.startswith("#"):
            m = re.match(r"(#{1,3})\s+(.*)", lines[0])
            level = len(m.group(1)) + 1  # --title owns h1
            out.append(f"<h{level}>{inline(m.group(2), rtl, store)}</h{level}>")
            rest = "\n".join(lines[1:]).strip()
            if rest:
                out.append(f"<p>{inline(rest, rtl, store)}</p>")
        elif all(l.lstrip().startswith(">") for l in lines):
            paras = [inline(l.lstrip()[1:].strip(), rtl, store) for l in lines]
            inner = "".join(f"<p>{p}</p>" for p in paras if p)
            out.append(f'<div class="callout">{inner}</div>')
        elif all(UL_ITEM.match(l.strip()) for l in lines):
            items = "".join(
                f"<li>{inline(UL_ITEM.sub('', l.strip(), count=1), rtl, store)}</li>"
                for l in lines
            )
            out.append(f"<ul>{items}</ul>")
        elif all(OL_ITEM.match(l.strip()) for l in lines):
            items = "".join(
                f"<li>{inline(OL_ITEM.sub('', l.strip(), count=1), rtl, store)}</li>"
                for l in lines
            )
            out.append(f"<ol>{items}</ol>")
        else:
            out.append(f"<p>{inline(' '.join(lines), rtl, store)}</p>")

    body = "\n".join(out)
    return PLACEHOLDER_RE.sub(lambda m: store[int(m.group(1))], body)


def warn_mixed_tokens(text: str) -> None:
    seen = set()
    for tok in MIXED_TOKEN.findall(text):
        if tok not in seen:
            seen.add(tok)
            print(f'WARN mixed RTL/Latin letters inside one word: "{tok}" — check for a stray Latin glyph')


def editor_open_cmd():
    """Return 'code' or 'cursor' when that editor has a click-free HTML
    preview configured (workbench.editorAssociations for *.html) and its CLI
    is on PATH. Otherwise None."""
    home = Path.home()
    if sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(home / "AppData" / "Roaming")))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
    candidates = [
        ("cursor", base / "Cursor" / "User" / "settings.json"),
        ("code", base / "Code" / "User" / "settings.json"),
    ]
    if "CURSOR_TRACE_ID" not in os.environ:
        candidates.reverse()  # prefer VS Code unless we're inside Cursor
    assoc = re.compile(r'"\*\.html"\s*:\s*"(?!default")')
    for cmd, settings in candidates:
        try:
            text = settings.read_text(encoding="utf-8")
        except OSError:
            continue
        if assoc.search(text) and shutil.which(cmd):
            return cmd
    return None


def open_page(path: Path, how: str) -> None:
    if how == "none":
        print("OPENED none")
        return
    if how in ("auto", "editor"):
        cmd = editor_open_cmd()
        if cmd:
            subprocess.Popen(
                [cmd, "--reuse-window", str(path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"OPENED editor ({cmd})")
            return
        if how == "editor":
            print("WARN no click-free editor preview configured; opening in browser instead")
    # Browser: always renders, never shows raw source.
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(path)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("OPENED browser")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate and open an explain-mode lesson page."
    )
    ap.add_argument("content", nargs="?", default="-",
                    help="content file (simple: markdown subset; rich: HTML fragment); '-' or omitted = stdin")
    ap.add_argument("--title", default="",
                    help="page title (required in simple mode; becomes <h1> and <title>)")
    ap.add_argument("--lang", default="en", help="learner's language code, e.g. he, ar, en")
    ap.add_argument("--dir", dest="direction", choices=["ltr", "rtl"],
                    help="text direction (default: derived from --lang)")
    ap.add_argument("--mode", choices=["simple", "rich"], default="simple")
    ap.add_argument("--open", dest="open_how",
                    choices=["auto", "browser", "editor", "none"],
                    help="how to open the page (default: auto, or $EXPLAIN_MODE_OPEN)")
    args = ap.parse_args()

    direction = args.direction or ("rtl" if args.lang.split("-")[0].lower() in RTL_LANGS else "ltr")
    rtl = direction == "rtl"
    open_how = args.open_how or os.environ.get("EXPLAIN_MODE_OPEN", "auto")
    if open_how not in ("auto", "browser", "editor", "none"):
        print(f"WARN ignoring invalid EXPLAIN_MODE_OPEN={open_how!r}")
        open_how = "auto"

    if args.content == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.content).read_text(encoding="utf-8")
    if not raw.strip():
        print("ERROR no content provided", file=sys.stderr)
        return 1
    if args.mode == "simple" and not args.title:
        print("ERROR --title is required in simple mode", file=sys.stderr)
        return 1

    if args.mode == "simple":
        body = md_to_html(raw, rtl)
        if rtl:
            warn_mixed_tokens(raw)
    else:
        body = raw.strip()
        if rtl:
            warn_mixed_tokens(re.sub(r"<[^>]+>", " ", body))

    store: list = []
    heading = ""
    if args.title:
        heading = f"<h1>{inline(args.title, rtl, store)}</h1>\n"
        heading = PLACEHOLDER_RE.sub(lambda m: store[int(m.group(1))], heading)

    root = repo_root()
    check_gitignore(root)
    path = page_path(root)
    path.write_text(
        PAGE.format(
            lang=html.escape(args.lang, quote=True),
            direction=direction,
            title_text=html.escape(
                f"{args.title.replace('`', '')} — explain-mode lesson"
                if args.title else "explain-mode lesson"
            ),
            css=CSS,
            heading=heading,
            body=body,
        ),
        encoding="utf-8",
    )
    print(f"PAGE {path}")
    open_page(path, open_how)
    return 0


if __name__ == "__main__":
    sys.exit(main())
