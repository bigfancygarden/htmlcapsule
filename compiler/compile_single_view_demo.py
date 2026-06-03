#!/usr/bin/env python3
"""
Compile a single-presentation demo Capsule.

Where compile_multiview_demo.py bakes every surface (reader/snap/feed/slides/
reel) into one Capsule and lets the host switch between them, this compiler
emits a Capsule that declares and renders exactly ONE presentation. The point
is to see each mobile presentation mode in isolation:

    --view snap   -> #capsule-mobile        profile "mobile"  navigation scroll
    --view feed   -> #capsule-mobile-feed   profile "mobile"  navigation scroll
    --view story  -> #capsule-reel          profile "reel"    navigation sequence

Each output is a self-contained, spec-valid Capsule (passes compiler/validate.py)
with a verifying integrity hash. Primary meaning stays readable without
JavaScript: snap/feed are pure CSS, and the story surface degrades to a stacked,
readable list until the runtime enhances it into an autoplaying reel.

Story chrome ownership: the story declares chrome "capsule" — it draws its own
progress bars, play/pause, and tap navigation. To stay escapable without a host
drawing competing chrome, it also ships the standard exit hatch: a control marked
`data-capsule-action="exit"` whose runtime asks the host to return to its top
level via, in order, `window.capsuleHost.exit()`, a `capsuleHost` WebKit message,
a `capsule:exit` postMessage to a parent frame, and finally `history.back()` /
`window.close()` when opened with no host at all. The hatch is host-neutral (no
HTML-Vault-specific API) and degrades gracefully standalone. Hosts are still
expected to keep their own unconditional escape as defense-in-depth.
"""

import argparse
import hashlib
import html
import json
from pathlib import Path

SPEC_VERSION = "0.3.0"
COMPILER_NAME = "compile_single_view_demo.py"
COMPILER_VERSION = "0.1.0"
HASH_PLACEHOLDER = "sha256:pending"

VIEWS = {
    "snap": {
        "entry": "#capsule-mobile",
        "profile": "mobile",
        "navigation": "scroll",
        "chrome": None,
        "capsule_profile": "static",
        "label": "Snap",
        "source_key": "sections",
    },
    "feed": {
        "entry": "#capsule-mobile-feed",
        "profile": "mobile",
        "navigation": "scroll",
        "chrome": None,
        "capsule_profile": "static",
        "label": "Feed",
        "source_key": "sections",
    },
    "story": {
        "entry": "#capsule-reel",
        "profile": "reel",
        "navigation": "sequence",
        "chrome": "capsule",
        "capsule_profile": "interactive",
        "label": "Story",
        "source_key": "cards",
    },
}


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_content_hash(manifest: dict, data: dict) -> str:
    manifest_for_hash = json.loads(json.dumps(manifest))
    manifest_for_hash.setdefault("integrity", {})
    manifest_for_hash["integrity"]["content_hash"] = HASH_PLACEHOLDER
    payload = canonical_json(manifest_for_hash) + "\n" + canonical_json(data)
    return f"sha256:{sha256_hex(payload)}"


def e(value) -> str:
    return html.escape(str(value), quote=True)


def load_source(path: Path, source_key: str) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    for field in ("uuid", "title", "description"):
        if field not in source:
            raise ValueError(f"missing required source field: {field}")
    items = source.get(source_key)
    if not items:
        raise ValueError(f"source must provide a non-empty '{source_key}' array for this view")
    return source


def build_presentation(view: str) -> dict:
    spec = VIEWS[view]
    presentation = {
        "id": view,
        "profile": spec["profile"],
        "entry": spec["entry"],
        "navigation": spec["navigation"],
        "title": spec["label"],
        "required": True,
    }
    if spec["chrome"] is not None:
        presentation["chrome"] = spec["chrome"]
    return presentation


def build_manifest(view: str, source: dict, item_count: int) -> dict:
    spec = VIEWS[view]
    return {
        "spec_version": SPEC_VERSION,
        "capsule_version": "1.0.0",
        "uuid": source["uuid"],
        "title": source["title"],
        "description": source["description"],
        "type": source.get("type", "briefing"),
        "profile": spec["capsule_profile"],
        "presentations": [build_presentation(view)],
        "created_at": source.get("created_at", "2026-06-03T00:00:00Z"),
        "generator": {"name": COMPILER_NAME, "version": COMPILER_VERSION, "kind": "compiler"},
        "source": {
            "origin": "spec_example",
            "snapshot_type": "fixture",
            "snapshot_id": source.get("snapshot_id", f"snapshot:single_{view}_demo"),
            "included_records": item_count,
            "spec_received": "v0.3.0 - 2026-05-19",
        },
        "privacy": {
            "visibility": source.get("visibility", "public"),
            "contains_private_data": False,
            "redaction_applied": False,
            "external_dependencies": False,
        },
        "integrity": {"content_hash": HASH_PLACEHOLDER, "hash_scope": "data+manifest"},
        "capabilities": ["about", "copy_as_json"],
    }


def build_data(view: str, source: dict) -> dict:
    spec = VIEWS[view]
    return {spec["source_key"]: source[spec["source_key"]]}


# ----------------------------------------------------------------------------
# Surfaces
# ----------------------------------------------------------------------------

def render_snap(source: dict) -> str:
    panels = []
    for index, section in enumerate(source["sections"], start=1):
        panels.append(
            f'<article class="snap-panel" data-source-section="{e(section["id"])}">'
            f'<span class="snap-index">{index:02d} / {len(source["sections"]):02d}</span>'
            f'<h2>{e(section["title"])}</h2>'
            f'<p>{e(section["body"])}</p></article>'
        )
    return (
        '<section id="capsule-mobile" class="snap-view" aria-label="Snap reading presentation">'
        f'{"".join(panels)}</section>'
    )


def render_feed(source: dict) -> str:
    cards = []
    for index, section in enumerate(source["sections"], start=1):
        cards.append(
            f'<article class="feed-card" data-source-section="{e(section["id"])}">'
            f'<span class="feed-index">{index:02d}</span>'
            f'<h2>{e(section["title"])}</h2>'
            f'<p>{e(section["body"])}</p></article>'
        )
    return (
        '<section id="capsule-mobile-feed" class="feed-view" aria-label="Feed presentation">'
        '<header class="feed-head">'
        '<p class="eyebrow">Feed</p>'
        f'<h1>{e(source["title"])}</h1>'
        f'<p>{e(source["description"])}</p></header>'
        f'<div class="feed-list">{"".join(cards)}</div></section>'
    )


def render_story(source: dict) -> str:
    cards = source["cards"]
    stories = []
    for index, card in enumerate(cards, start=1):
        heading = "h1" if index == 1 else "h2"
        active = " is-active" if index == 1 else ""
        stories.append(
            f'<article class="story{active}" data-card-id="{e(card["id"])}">'
            f'<div class="story-content">'
            f'<p class="story-kicker">{e(card.get("role", "story"))}</p>'
            f'<{heading} class="story-headline">{e(card["title"])}</{heading}>'
            f'<p class="story-body">{e(card["body"])}</p>'
            f'</div></article>'
        )
    return (
        '<section id="capsule-reel" class="reel" aria-label="Story presentation">'
        '<div class="story-progress" id="story-progress" aria-hidden="true"></div>'
        '<div class="story-controls">'
        '<button id="story-pause" type="button" class="story-ctl" aria-label="Pause story">&#10074;&#10074;</button>'
        '<span class="story-controls-spacer"></span>'
        '<button data-capsule-action="exit" type="button" class="story-ctl story-exit" aria-label="Close and return to vault">&#10005;</button>'
        '</div>'
        f'<div class="story-deck">{"".join(stories)}</div></section>'
    )


def render_surface(view: str, source: dict) -> str:
    if view == "snap":
        return render_snap(source)
    if view == "feed":
        return render_feed(source)
    return render_story(source)


UTILITY_BLOCK = """
<section class="utility" aria-label="Capsule utilities">
  <details id="about">
    <summary>About this capsule</summary>
    <div class="about-panel">
      <button data-capsule-action="copy_as_json" type="button">Copy JSON</button>
      <pre id="about-data"></pre>
    </div>
  </details>
</section>
""".strip()


# ----------------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------------

STYLE_COMMON = """
:root {
  color-scheme: light;
  --ink: #111827;
  --muted: #5b6472;
  --line: #d7dee8;
  --paper: #f7f8f5;
  --teal: #0f766e;
  --rose: #be123c;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.5;
  -webkit-text-size-adjust: 100%;
}
#capsule-root { display: block; }
.eyebrow {
  margin: 0 0 .55rem;
  color: var(--teal);
  font-size: .76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .02em;
}
.utility {
  padding: 1.25rem 1.15rem 2.5rem;
  color: var(--muted);
  font-size: .82rem;
  background: var(--paper);
}
.utility summary { cursor: pointer; width: fit-content; }
.about-panel { display: flex; gap: .6rem; align-items: flex-start; margin-top: .65rem; }
.utility button {
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #fff;
  padding: .35rem .55rem;
  font: inherit;
  cursor: pointer;
}
.utility pre {
  max-width: 100%;
  max-height: 12rem;
  overflow: auto;
  margin: 0;
  padding: .5rem;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #fff;
}
"""

STYLE_SNAP = """
html { scroll-snap-type: y mandatory; }
.snap-view { display: block; }
.snap-panel {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: .9rem;
  padding: max(4rem, env(safe-area-inset-top)) 1.4rem max(2.5rem, env(safe-area-inset-bottom));
  scroll-snap-align: start;
  scroll-snap-stop: always;
  border-bottom: 1px solid var(--line);
}
.snap-panel:nth-child(5n+1) { background: linear-gradient(165deg, #ffffff, #eaf8f5); }
.snap-panel:nth-child(5n+2) { background: linear-gradient(165deg, #ffffff, #fff1cf); }
.snap-panel:nth-child(5n+3) { background: linear-gradient(165deg, #ffffff, #ecebff); }
.snap-panel:nth-child(5n+4) { background: linear-gradient(165deg, #ffffff, #ffe4eb); }
.snap-panel:nth-child(5n+5) { background: linear-gradient(165deg, #ffffff, #e3f0ff); }
.snap-index {
  width: fit-content;
  padding: .3rem .5rem;
  border-radius: 999px;
  background: rgba(15,118,110,.12);
  color: var(--teal);
  font-size: .76rem;
  font-weight: 850;
  line-height: 1;
}
.snap-panel h2 {
  max-width: 12ch;
  margin: 0;
  font-size: clamp(2.4rem, 12vw, 3.8rem);
  line-height: .96;
  letter-spacing: -0.01em;
}
.snap-panel p {
  max-width: 26rem;
  margin: 0;
  color: #303846;
  font-size: clamp(1.05rem, 4.6vw, 1.3rem);
  line-height: 1.34;
}
"""

STYLE_FEED = """
.feed-view {
  display: block;
  padding: max(1.25rem, env(safe-area-inset-top)) 1rem max(2rem, env(safe-area-inset-bottom));
}
.feed-head {
  padding: 1.1rem;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: linear-gradient(160deg, #fff, #f3fbf8);
}
.feed-head h1 {
  margin: .1rem 0 .5rem;
  font-size: clamp(2.1rem, 10vw, 3rem);
  line-height: .96;
  letter-spacing: -0.01em;
}
.feed-head > p:not(.eyebrow) { margin: 0; color: #303846; font-size: .98rem; line-height: 1.35; }
.feed-list { display: grid; gap: .8rem; margin-top: .85rem; }
.feed-card {
  padding: 1rem 1.05rem;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #fff;
}
.feed-index {
  display: inline-flex;
  margin-bottom: .55rem;
  padding: .25rem .5rem;
  border-radius: 999px;
  background: rgba(15,118,110,.1);
  color: var(--teal);
  font-size: .74rem;
  font-weight: 850;
  line-height: 1;
}
.feed-card h2 { margin: 0 0 .35rem; font-size: 1.32rem; line-height: 1.12; letter-spacing: -0.01em; }
.feed-card p { margin: 0; color: var(--muted); font-size: .98rem; line-height: 1.4; }
"""

STYLE_STORY = """
.reel { display: block; background: #05060a; color: #fff; }
.story-progress { display: none; }
.story-controls { display: none; }
/* No-JS fallback: a readable, stacked list of story cards. */
.reel:not(.story-enhanced) .story-deck { display: block; }
.reel:not(.story-enhanced) .story {
  padding: 2.6rem 1.4rem;
  border-bottom: 1px solid rgba(255,255,255,.1);
}
.story-kicker {
  margin: 0 0 .7rem;
  color: #ffd1dc;
  font-size: .82rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.story-headline {
  max-width: 12ch;
  margin: 0;
  font-size: clamp(2.6rem, 13vw, 4rem);
  font-weight: 850;
  line-height: .92;
  letter-spacing: -0.01em;
}
.story-body {
  max-width: 22rem;
  margin: 1rem 0 0;
  color: #e7e9ef;
  font-size: clamp(1.1rem, 4.8vw, 1.4rem);
  line-height: 1.3;
}
/* Enhanced (runtime present): an autoplaying full-screen reel. */
.reel.story-enhanced {
  position: relative;
  height: 100dvh;
  min-height: 100dvh;
  overflow: hidden;
}
.reel.story-enhanced .story-deck { position: absolute; inset: 0; }
.reel.story-enhanced .story {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: max(5rem, calc(env(safe-area-inset-top) + 4.5rem)) 1.5rem max(4rem, calc(env(safe-area-inset-bottom) + 3.5rem));
  border: 0;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity .32s ease;
}
.reel.story-enhanced .story.is-active { opacity: 1; visibility: visible; pointer-events: auto; }
.reel.story-enhanced .story:nth-child(5n+1) { background: linear-gradient(165deg, #1d2233, #3b1d2b); }
.reel.story-enhanced .story:nth-child(5n+2) { background: linear-gradient(165deg, #112a2b, #1d3b36); }
.reel.story-enhanced .story:nth-child(5n+3) { background: linear-gradient(165deg, #2a2440, #1d1f3b); }
.reel.story-enhanced .story:nth-child(5n+4) { background: linear-gradient(165deg, #3b2740, #2b1d3b); }
.reel.story-enhanced .story:nth-child(5n+5) { background: linear-gradient(165deg, #3b3320, #2b2a1d); }
.reel.story-enhanced .story.is-active .story-kicker { animation: story-rise .5s 40ms both; }
.reel.story-enhanced .story.is-active .story-headline { animation: story-rise .55s 110ms both; }
.reel.story-enhanced .story.is-active .story-body { animation: story-rise .6s 190ms both; }
@keyframes story-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.reel.story-enhanced .story-progress {
  position: absolute;
  top: max(.6rem, calc(env(safe-area-inset-top) + .35rem));
  left: max(.7rem, env(safe-area-inset-left));
  right: max(.7rem, env(safe-area-inset-right));
  z-index: 5;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: .28rem;
  pointer-events: none;
}
.reel.story-enhanced .story-progress span {
  position: relative;
  height: 3px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255,255,255,.28);
}
.reel.story-enhanced .story-progress i {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: #fff;
  transform: scaleX(var(--fill, 0));
  transform-origin: left;
}
.reel.story-enhanced .story-controls {
  position: absolute;
  top: max(1.4rem, calc(env(safe-area-inset-top) + 1rem));
  left: max(.8rem, env(safe-area-inset-left));
  right: max(.8rem, env(safe-area-inset-right));
  z-index: 6;
  display: flex;
  align-items: center;
  gap: .6rem;
}
.story-controls-spacer { flex: 1; }
.story-ctl {
  width: 44px;
  height: 44px;
  display: inline-grid;
  place-items: center;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: rgba(255,255,255,.16);
  color: #fff;
  font-size: 1.05rem;
  line-height: 1;
  cursor: pointer;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  touch-action: manipulation;
}
.story-ctl:active { background: rgba(255,255,255,.3); }
@media (prefers-reduced-motion: reduce) {
  .reel.story-enhanced .story.is-active .story-kicker,
  .reel.story-enhanced .story.is-active .story-headline,
  .reel.story-enhanced .story.is-active .story-body { animation: none; }
  .reel.story-enhanced .story { transition: none; }
}
"""


def render_style(view: str) -> str:
    per_view = {"snap": STYLE_SNAP, "feed": STYLE_FEED, "story": STYLE_STORY}[view]
    return (STYLE_COMMON + per_view).strip()


# ----------------------------------------------------------------------------
# Runtime
# ----------------------------------------------------------------------------

RUNTIME_ABOUT = """
  var about = document.getElementById("about-data");
  var data = JSON.parse(document.getElementById("capsule-data").textContent);
  if (about) about.textContent = JSON.stringify(data, null, 2);
  var copy = document.querySelector('[data-capsule-action="copy_as_json"]');
  if (copy) copy.addEventListener("click", function(){
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  });
"""

RUNTIME_STORY = """
  var reel = document.getElementById("capsule-reel");
  if (!reel) return;
  var stories = Array.prototype.slice.call(reel.querySelectorAll(".story"));
  if (!stories.length) return;
  reel.classList.add("story-enhanced");

  var progress = document.getElementById("story-progress");
  var pauseBtn = document.getElementById("story-pause");
  var exitBtn = reel.querySelector('[data-capsule-action="exit"]');
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var DURATION = 5000;
  var idx = 0, elapsed = 0, last = 0, paused = false, ended = false, raf = 0;
  var fills = [];

  stories.forEach(function(){
    var span = document.createElement("span");
    var fill = document.createElement("i");
    span.appendChild(fill);
    progress.appendChild(span);
    fills.push(fill);
  });

  function setFill(i, fraction){ if (fills[i]) fills[i].style.setProperty("--fill", fraction); }
  function paint(){
    fills.forEach(function(_, i){
      setFill(i, i < idx ? 1 : (i === idx ? Math.min(elapsed / DURATION, 1) : 0));
    });
  }
  function syncPauseIcon(){
    if (!pauseBtn) return;
    var playing = !paused && !ended;
    pauseBtn.innerHTML = playing ? "&#10074;&#10074;" : "&#9658;";
    pauseBtn.setAttribute("aria-label", playing ? "Pause story" : "Play story");
  }
  function activate(n){
    idx = Math.max(0, Math.min(n, stories.length - 1));
    elapsed = 0; last = 0; ended = false;
    stories.forEach(function(story, i){ story.classList.toggle("is-active", i === idx); });
    paint(); syncPauseIcon();
  }
  function finish(){
    ended = true; paused = true;
    setFill(stories.length - 1, 1);
    if (raf) cancelAnimationFrame(raf);
    raf = 0; syncPauseIcon();
  }
  function next(){ if (idx < stories.length - 1) activate(idx + 1); else finish(); }
  function prev(){ if (idx > 0) activate(idx - 1); else activate(0); }
  function frame(now){
    raf = requestAnimationFrame(frame);
    if (paused){ last = now; return; }
    var delta = last ? now - last : 0;
    last = now;
    elapsed += delta;
    setFill(idx, Math.min(elapsed / DURATION, 1));
    if (elapsed >= DURATION) next();
  }
  function play(){
    if (ended) activate(0);
    paused = false;
    if (!raf) raf = requestAnimationFrame(frame);
    syncPauseIcon();
  }
  function toggle(){
    if (ended){ activate(0); play(); return; }
    paused = !paused;
    if (!paused && !raf) raf = requestAnimationFrame(frame);
    syncPauseIcon();
  }

  // Standard host-neutral exit hatch. Tries, in order: a host capability object,
  // a WebKit message channel, a parent-frame postMessage, then a standalone
  // fallback. Works inside HTML Vault, any other compliant host, or opened raw.
  function requestExit(){
    try { if (window.capsuleHost && typeof window.capsuleHost.exit === "function") { window.capsuleHost.exit(); return; } } catch (e) {}
    try { if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.capsuleHost) { window.webkit.messageHandlers.capsuleHost.postMessage({ type: "exit" }); return; } } catch (e) {}
    try { if (window.parent && window.parent !== window) { window.parent.postMessage({ type: "capsule:exit" }, "*"); return; } } catch (e) {}
    if (window.history.length > 1) { window.history.back(); return; }
    try { window.close(); } catch (e) {}
  }

  if (pauseBtn) pauseBtn.addEventListener("click", function(event){ event.stopPropagation(); toggle(); });
  if (exitBtn) exitBtn.addEventListener("click", function(event){ event.stopPropagation(); requestExit(); });
  reel.addEventListener("click", function(event){
    if (event.target.closest('#story-pause, [data-capsule-action="exit"]')) return;
    var rect = reel.getBoundingClientRect();
    var relativeX = (event.clientX - rect.left) / rect.width;
    if (relativeX < 0.33) prev(); else next();
  });
  document.addEventListener("keydown", function(event){
    if (event.key === "ArrowLeft") prev();
    else if (event.key === "ArrowRight") next();
    else if (event.key === " "){ event.preventDefault(); toggle(); }
    else if (event.key === "Escape") requestExit();
  });
  document.addEventListener("visibilitychange", function(){ if (document.hidden) paused = true; });

  activate(0);
  if (reduce) { paused = true; syncPauseIcon(); } else play();
"""


def render_runtime(view: str) -> str:
    body = RUNTIME_ABOUT
    if view == "story":
        body = body + RUNTIME_STORY
    return "(function(){" + body + "})();"


# ----------------------------------------------------------------------------
# Assembly
# ----------------------------------------------------------------------------

def render_html(view: str, manifest: dict, data: dict, source: dict) -> str:
    spec = VIEWS[view]
    default_mode = {"snap": "scroll", "feed": "feed", "story": "present"}[view]
    viewport = "width=device-width, initial-scale=1.0, viewport-fit=cover"
    if view == "story":
        viewport = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"
    csp = (
        "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
        "img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="{viewport}">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<title>{e(source["title"])}</title>
<script id="capsule-manifest" type="application/json">{json.dumps(manifest, indent=2)}</script>
<script id="capsule-data" type="application/json">{json.dumps(data, indent=2)}</script>
<style id="capsule-style">{render_style(view)}</style>
</head>
<body>
<main id="capsule-root" data-view-mode="{default_mode}" data-presentation="{spec['label']}">
{render_surface(view, source)}
{UTILITY_BLOCK}
</main>
<script id="capsule-runtime">{render_runtime(view)}</script>
</body>
</html>
"""


def compile_source(view: str, source_path: Path, output_path: Path) -> dict:
    spec = VIEWS[view]
    source = load_source(source_path, spec["source_key"])
    items = source[spec["source_key"]]
    manifest = build_manifest(view, source, len(items))
    data = build_data(view, source)
    manifest["integrity"]["content_hash"] = compute_content_hash(manifest, data)
    html_text = render_html(view, manifest, data, source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    return {"output": str(output_path), "uuid": manifest["uuid"], "bytes": output_path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a single-presentation demo Capsule.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--view", required=True, choices=sorted(VIEWS.keys()))
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    result = compile_source(args.view, args.source, args.output)
    print(f"Compiled {result['output']}")
    print(f"  view: {args.view}")
    print(f"  uuid: {result['uuid']}")
    print(f"  file size: {result['bytes']:,} bytes")


if __name__ == "__main__":
    main()
