#!/usr/bin/env python3
"""
Compile a multi-view Capsule experiment from sections, cards, and assets.

This is intentionally narrow: it proves that one source model can emit one
sealed Capsule with reader, mobile, slides, and a native-feeling story surface.
"""

import argparse
import hashlib
import html
import json
from pathlib import Path

SPEC_VERSION = "0.3.0"
COMPILER_NAME = "compile_multiview_demo.py"
COMPILER_VERSION = "0.1.0"
HASH_PLACEHOLDER = "sha256:pending"


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


def load_source(path: Path) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    for field in ("uuid", "title", "description", "sections", "presentation_model"):
        if field not in source:
            raise ValueError(f"missing required source field: {field}")
    cards = source["presentation_model"].get("cards", [])
    if not cards:
        raise ValueError("presentation_model.cards must not be empty")
    return source


def build_manifest(source: dict) -> dict:
    return {
        "spec_version": SPEC_VERSION,
        "capsule_version": "1.0.0",
        "uuid": source["uuid"],
        "title": source["title"],
        "description": source["description"],
        "type": source.get("type", "briefing"),
        "profile": "interactive",
        "presentations": [
            {"id": "reader", "profile": "reader", "entry": "#capsule-root", "navigation": "scroll", "required": True},
            {"id": "mobile", "profile": "mobile", "entry": "#capsule-mobile", "navigation": "scroll", "required": True},
            {"id": "mobile_feed", "profile": "mobile", "entry": "#capsule-mobile-feed", "navigation": "scroll", "required": True},
            {"id": "desktop_slides", "profile": "slides", "entry": "#capsule-slides", "navigation": "paged", "chrome": "capsule", "required": True},
            {"id": "mobile_story", "profile": "reel", "entry": "#capsule-reel", "navigation": "sequence", "chrome": "capsule", "required": True},
        ],
        "created_at": source.get("created_at", "2026-06-01T00:00:00Z"),
        "generator": {"name": COMPILER_NAME, "version": COMPILER_VERSION, "kind": "compiler"},
        "source": {
            "origin": "spec_example",
            "snapshot_type": "fixture",
            "snapshot_id": source.get("snapshot_id", "snapshot:multiview_demo"),
            "included_records": len(source["sections"]),
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


def build_data(source: dict) -> dict:
    return {
        "sections": source["sections"],
        "assets": source.get("assets", []),
        "presentation_model": source["presentation_model"],
    }


def render_asset_defs() -> str:
    return """<svg class="asset-defs" aria-hidden="true" width="0" height="0" focusable="false">
  <symbol id="asset-flow" viewBox="0 0 640 360">
    <rect width="640" height="360" rx="28" fill="#f8fafc"/>
    <path d="M94 178h452" stroke="#94a3b8" stroke-width="8" stroke-linecap="round"/>
    <g fill="#ffffff" stroke-width="4">
      <rect x="52" y="96" width="128" height="164" rx="18" stroke="#0f766e"/>
      <rect x="204" y="96" width="128" height="164" rx="18" stroke="#be123c"/>
      <rect x="356" y="96" width="128" height="164" rx="18" stroke="#4f46e5"/>
      <rect x="508" y="96" width="80" height="164" rx="22" stroke="#b45309"/>
    </g>
    <g font-family="system-ui, sans-serif" font-weight="800" font-size="24" text-anchor="middle" fill="#111827">
      <text x="116" y="160">reader</text>
      <text x="268" y="160">mobile</text>
      <text x="420" y="160">slides</text>
      <text x="548" y="154">reel</text>
    </g>
    <g font-family="system-ui, sans-serif" font-size="16" text-anchor="middle" fill="#64748b">
      <text x="116" y="197">scroll</text>
      <text x="268" y="197">scroll</text>
      <text x="420" y="197">screen</text>
      <text x="548" y="191">story</text>
    </g>
    <circle cx="320" cy="300" r="18" fill="#111827"/>
    <text x="320" y="306" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle" fill="#fff">1x</text>
    <text x="320" y="334" font-family="system-ui, sans-serif" font-size="17" text-anchor="middle" fill="#475569">shared sections / cards / assets</text>
  </symbol>
</svg>"""


def render_svg_use(asset_id: str, label: str, class_name: str = "asset-figure") -> str:
    return (
        f'<figure class="{class_name}">'
        f'<svg role="img" aria-label="{e(label)}" viewBox="0 0 640 360">'
        f'<use href="#asset-{e(asset_id)}"></use>'
        f'</svg></figure>'
    )


def render_reader(source: dict) -> str:
    sections = []
    for section in source["sections"]:
        sections.append(
            f'<section class="reader-section" id="section-{e(section["id"])}" data-source-section="{e(section["id"])}">'
            f'<h2>{e(section["title"])}</h2><p>{e(section["body"])}</p></section>'
        )
    return (
        '<section class="reader-view" aria-labelledby="reader-title">'
        '<p class="eyebrow">Reader</p>'
        f'<h1 id="reader-title">{e(source["title"])}</h1>'
        f'<p class="lede">{e(source["description"])}</p>'
        f'{render_svg_use("flow", "Four presentation surfaces derived from one source model.")}'
        f'{"".join(sections)}</section>'
    )


def render_mobile(source: dict) -> str:
    items = []
    for index, section in enumerate(source["sections"], start=1):
        section_id = f'mobile-{section["id"]}'
        items.append(
            f'<article class="mobile-item" id="{e(section_id)}" data-source-section="{e(section["id"])}">'
            f'<span class="mobile-index">{index:02d}</span>'
            f'<div class="mobile-copy"><h3>{e(section["title"])}</h3><p>{e(section["body"])}</p></div></article>'
    )
    return (
        '<section id="capsule-mobile" class="mobile-view" aria-label="Mobile reading presentation">'
        '<header class="mobile-hero" id="mobile-overview">'
        '<p class="eyebrow">Briefing</p>'
        f'<h2>{e(source["title"])}</h2>'
        f'<p>{e(source["description"])}</p>'
        f'{render_svg_use("flow", "Four presentation surfaces derived from one source model.", "mobile-asset")}'
        '</header>'
        f'<div class="mobile-scroll-track">{"".join(items)}</div></section>'
    )


def render_mobile_feed(source: dict) -> str:
    cards = []
    for index, section in enumerate(source["sections"], start=1):
        cards.append(
            f'<article class="feed-card" id="feed-{e(section["id"])}" data-source-section="{e(section["id"])}">'
            f'<span class="feed-index">{index:02d}</span>'
            f'<h3>{e(section["title"])}</h3>'
            f'<p>{e(section["body"])}</p>'
            f'<a href="#mobile-{e(section["id"])}">Snap section</a></article>'
        )
    return (
        '<section id="capsule-mobile-feed" class="feed-view" aria-label="Mobile feed presentation">'
        '<header class="feed-header">'
        '<p class="eyebrow">Feed</p>'
        f'<h2>{e(source["title"])}</h2>'
        f'<p>{e(source["description"])}</p></header>'
        f'<div class="feed-list">{"".join(cards)}</div></section>'
    )


def render_slides(source: dict) -> str:
    cards = source["presentation_model"]["cards"]
    slides = []
    total = len(cards)
    for index, card in enumerate(cards, start=1):
        source_sections = " ".join(card.get("source_sections", []))
        art = render_svg_use("flow", "Shared presentation model diagram.", "slide-asset") if "flow" in card.get("asset_refs", []) else ""
        slides.append(
            f'<article class="slide" data-card-id="{e(card["id"])}" data-source-section="{e(source_sections)}">'
            f'<div><p class="eyebrow">Slide {index:02d}</p><h3>{e(card["title"])}</h3>'
            f'<p>{e(card["body"])}</p></div>{art}<footer>{index} / {total}</footer></article>'
        )
    return (
        '<section id="capsule-slides" class="slides-view" aria-label="Desktop slides presentation" tabindex="-1" style="--slide-index:0">'
        f'<div class="slide-track">{"".join(slides)}</div>'
        '<div class="slide-controls" aria-label="Slide controls">'
        '<button type="button" class="slide-nav" id="slide-prev" aria-label="Previous slide">&lt;</button>'
        '<span id="slide-status">1 / 1</span>'
        '<button type="button" class="slide-nav" id="slide-next" aria-label="Next slide">&gt;</button>'
        '</div></section>'
    )


def render_reel(source: dict) -> str:
    cards = source["presentation_model"]["cards"]
    stories = []
    for index, card in enumerate(cards, start=1):
        source_sections = " ".join(card.get("source_sections", []))
        heading_tag = "h1" if index == 1 else "h2"
        art = render_svg_use("flow", "Shared presentation model diagram.", "story-asset") if "flow" in card.get("asset_refs", []) else ""
        active = " is-active" if index == 1 else ""
        stories.append(
            f'<article class="story{active}" data-card-id="{e(card["id"])}" data-source-section="{e(source_sections)}">'
            f'<div class="story-content"><p class="story-kicker">{e(card.get("role", "story"))}</p>'
            f'<{heading_tag} class="story-headline">{e(card["title"])}</{heading_tag}>'
            f'<p class="story-body">{e(card["body"])}</p>{art}</div></article>'
        )
    return f"""
<section id="capsule-reel" class="reel-view" aria-label="Mobile story presentation">
  <div class="story-phone" aria-label="Story sequence">
    <div class="story-backdrop" aria-hidden="true"></div>
    <div class="story-screen" aria-live="polite">
      <div class="story-progress-shell" id="story-progress" aria-hidden="true"></div>
      <div class="story-header">
        <span class="story-avatar"><b>HC</b></span>
        <div class="story-meta"><span class="story-name">capsule</span><span class="story-time">now</span></div>
        <span class="story-spacer"></span>
        <button class="story-icon" id="story-pause" type="button" aria-label="Pause">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>
        </button>
        <button class="story-icon" id="story-close" type="button" aria-label="Close story view">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>
      <div class="story-deck" id="story-deck">{"".join(stories)}</div>
      <div class="story-pause-pill" aria-hidden="true">Paused</div>
      <button class="story-replay" id="story-replay" type="button">Back to start</button>
    </div>
  </div>
</section>
""".strip()


def render_view_switcher() -> str:
    return """
<nav class="view-switcher" aria-label="View mode">
  <button class="view-option" type="button" data-view-target="scroll" aria-pressed="true"><span class="desktop-label">Reader</span><span class="mobile-label">Snap</span></button>
  <button class="view-option mobile-feed-option" type="button" data-view-target="feed" aria-pressed="false">Feed</button>
  <button class="view-option" type="button" data-view-target="present" aria-pressed="false"><span class="desktop-label">Slides</span><span class="mobile-label">Story</span></button>
</nav>
""".strip()


def render_style() -> str:
    return """
:root {
  color-scheme: light;
  --ink: #111827;
  --muted: #5b6472;
  --line: #d7dee8;
  --paper: #f7f8f5;
  --panel: #fff;
  --teal: #0f766e;
  --rose: #be123c;
  --gold: #e8bb49;
  --lav: #d9d5ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.55;
}
html.is-deck-mode,
html.is-deck-mode body {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
main { max-width: 74rem; margin: 0 auto; padding: 2rem 1rem 4rem; }
.asset-defs { position: absolute; width: 0; height: 0; overflow: hidden; }
.view-switcher {
  position: sticky;
  top: .65rem;
  z-index: 10;
  display: inline-flex;
  float: right;
  gap: .12rem;
  margin: 0 0 .85rem .85rem;
  padding: .16rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(10px);
}
.view-switcher button {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--muted);
  padding: .28rem .52rem;
  font: inherit;
  font-size: .76rem;
  font-weight: 760;
  cursor: pointer;
}
.view-switcher button[aria-pressed=true] { background: var(--ink); color: #fff; }
.view-switcher button:focus-visible { outline: 3px solid rgba(17,24,39,.35); outline-offset: 2px; }
.reader-view, .mobile-view, .feed-view, .slides-view, .reel-view { display: none; }
.mobile-label, .mobile-feed-option { display: none; }
.eyebrow {
  margin: 0 0 .6rem;
  color: var(--teal);
  font-size: .78rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}
.lede { max-width: 54rem; color: var(--muted); font-size: 1.1rem; }
.reader-view h1 {
  margin: .2rem 0 1rem;
  font-size: clamp(2.2rem,5vw,4.6rem);
  letter-spacing: 0;
  line-height: 1;
}
.reader-section { max-width: 52rem; border-top: 1px solid var(--line); padding: 1rem 0; }
.reader-section h2, .mobile-item h3 { margin: 0 0 .35rem; }
.reader-section p, .mobile-item p { margin: 0; color: var(--muted); }
.asset-figure { max-width: 44rem; margin: 1.5rem 0; }
.asset-figure svg, .slide-asset svg, .story-asset svg { display: block; width: 100%; height: auto; }
.mobile-view {
  max-width: 25rem;
  margin: 0 0 2rem;
  padding: 0;
}
.mobile-hero {
  padding: .9rem .9rem .95rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(160deg,#fff,#f3fbf8);
}
.mobile-hero h2 {
  max-width: 10ch;
  margin: .15rem 0 .6rem;
  font-size: clamp(2rem,10.5vw,2.9rem);
  line-height: .95;
  letter-spacing: 0;
}
.mobile-hero > p:not(.eyebrow) {
  margin: 0;
  color: #303846;
  font-size: .97rem;
  line-height: 1.36;
}
.mobile-asset {
  width: 72%;
  max-width: 15rem;
  margin: .85rem 0 0;
  overflow: hidden;
  border-radius: 8px;
  background: #f8fafc;
}
.mobile-scroll-track {
  display: grid;
  gap: .48rem;
  margin-top: .75rem;
}
.mobile-item {
  display: grid;
  grid-template-columns: 1.85rem 1fr;
  gap: .62rem;
  padding: .72rem .78rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,.78);
}
.mobile-index {
  color: var(--teal);
  font-size: .78rem;
  font-weight: 850;
  line-height: 1.8;
}
.mobile-item h3 {
  margin: 0 0 .25rem;
  font-size: 1.08rem;
  line-height: 1.18;
  letter-spacing: 0;
}
.mobile-item p { font-size: .95rem; line-height: 1.38; }
.feed-view {
  max-width: 28rem;
  margin: 0 0 2rem;
  padding: 0;
}
.feed-header {
  padding: 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(160deg,#fff,#f8fafc);
}
.feed-header h2 {
  margin: .15rem 0 .55rem;
  font-size: clamp(2rem,10vw,2.8rem);
  line-height: .95;
  letter-spacing: 0;
}
.feed-header > p:not(.eyebrow) {
  margin: 0;
  color: #303846;
  font-size: .97rem;
  line-height: 1.36;
}
.feed-list {
  display: grid;
  gap: .7rem;
  margin-top: .8rem;
}
.feed-card {
  padding: .9rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,.86);
}
.feed-index {
  display: inline-flex;
  margin-bottom: .6rem;
  color: var(--teal);
  font-size: .76rem;
  font-weight: 850;
}
.feed-card h3 {
  margin: 0 0 .35rem;
  font-size: 1.28rem;
  line-height: 1.12;
  letter-spacing: 0;
}
.feed-card p {
  margin: 0;
  color: var(--muted);
  font-size: .96rem;
  line-height: 1.4;
}
.feed-card a {
  display: inline-flex;
  margin-top: .7rem;
  color: var(--teal);
  font-size: .78rem;
  font-weight: 800;
  text-decoration: none;
}
.slides-view {
  position: relative;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  background: #202532;
  margin: 0 -1rem;
  padding: 1rem;
}
.slide-track {
  display: flex;
  gap: 1rem;
}
.slide-controls {
  display: none;
}
.slide {
  position: relative;
  flex: 0 0 min(100%,58rem);
  aspect-ratio: 16 / 9;
  scroll-snap-align: start;
  display: grid;
  grid-template-columns: 1.1fr .8fr;
  gap: 1.5rem;
  align-items: center;
  padding: clamp(1.4rem,4vw,3.5rem);
  border-radius: 8px;
  background: linear-gradient(135deg,#fff,#eef8f5 62%,#f8ecd2);
  box-shadow: 0 1rem 3rem rgba(0,0,0,.25);
}
.slide h3 {
  margin: 0;
  font-size: clamp(2.2rem,6vw,4.7rem);
  letter-spacing: 0;
  line-height: .96;
}
.slide p { max-width: 34rem; color: #303846; font-size: clamp(1rem,1.9vw,1.45rem); }
.slide footer { position: absolute; right: 1rem; bottom: 1rem; color: #64748b; }
.slide-asset { margin: 0; }
.reel-view { margin: 0 auto; }
.story-phone {
  position: relative;
  width: min(100%, 25rem);
  height: min(44rem, calc(100dvh - 6rem));
  min-height: 34rem;
  margin: 0 auto;
  background: #05060a;
  border-radius: 2rem;
  overflow: hidden;
  color: var(--ink);
  touch-action: manipulation;
  user-select: none;
}
.story-backdrop { position: absolute; inset: 0; background: #05060a; pointer-events: none; }
.story-screen {
  position: relative;
  z-index: 1;
  height: 100%;
  overflow: hidden;
  background: #fffdf8;
  transform: translateY(var(--dismiss-y, 0)) scale(var(--dismiss-scale, 1));
  transform-origin: 50% 100%;
  transition: transform 260ms cubic-bezier(.22,.61,.36,1), opacity 200ms ease;
}
.story-screen.is-dragging { transition: none; }
.story-deck { position: absolute; inset: 0; }
.story {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-rows: 1fr;
  padding: 5.2rem 1.15rem 4.2rem;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
.story.is-active { opacity: 1; visibility: visible; pointer-events: auto; }
.story:nth-child(1) { background: linear-gradient(160deg,#fff7f9 0%,#ffdce4 100%); }
.story:nth-child(2) { background: linear-gradient(160deg,#f2fffb 0%,#cdeee8 100%); }
.story:nth-child(3) { background: linear-gradient(160deg,#fffdf3 0%,#eef3b5 100%); }
.story:nth-child(4) { background: linear-gradient(160deg,#f7f5ff 0%,#d9d5ff 100%); }
.story:nth-child(5) { background: linear-gradient(160deg,#fffaf0 0%,#f4d7b5 100%); }
.story-content {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 1;
}
.story.is-active .story-kicker { animation: story-rise 520ms 40ms both cubic-bezier(.2,.7,.2,1); }
.story.is-active .story-headline { animation: story-rise 560ms 110ms both cubic-bezier(.2,.7,.2,1); }
.story.is-active .story-body, .story.is-active .story-asset { animation: story-rise 600ms 190ms both cubic-bezier(.2,.7,.2,1); }
@keyframes story-rise {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}
.story-kicker {
  margin: 0 0 .7rem;
  color: var(--rose);
  font-size: clamp(.78rem,3.2vw,.95rem);
  font-weight: 850;
  letter-spacing: 0;
  line-height: 1;
  text-transform: uppercase;
}
.story-headline {
  max-width: 8.5ch;
  margin: 0;
  font-size: clamp(3.1rem,15vw,5.3rem);
  font-weight: 880;
  letter-spacing: 0;
  line-height: .9;
}
.story-body {
  max-width: 18rem;
  margin: clamp(.9rem,3dvh,1.4rem) 0 0;
  color: #292f3b;
  font-size: clamp(1.08rem,4.6vw,1.38rem);
  line-height: 1.28;
}
.story-asset { width: min(100%, 18rem); margin: 1.2rem 0 0; }
.story-progress-shell {
  position: absolute;
  top: max(.55rem, calc(env(safe-area-inset-top) + .35rem));
  right: max(.7rem, env(safe-area-inset-right));
  left: max(.7rem, env(safe-area-inset-left));
  z-index: 5;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: .26rem;
  pointer-events: none;
}
.story-progress-shell span {
  position: relative;
  height: .2rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(17,20,28,.22);
}
.story-progress-shell i {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--ink);
  transform: scaleX(var(--fill, 0));
  transform-origin: left;
}
.story-header {
  position: absolute;
  top: max(1.25rem, calc(env(safe-area-inset-top) + 1.05rem));
  right: max(.85rem, env(safe-area-inset-right));
  left: max(.95rem, env(safe-area-inset-left));
  z-index: 5;
  display: flex;
  align-items: center;
  gap: .6rem;
  color: var(--ink);
}
.story-avatar {
  display: grid;
  width: 2.05rem;
  height: 2.05rem;
  flex: none;
  padding: 2px;
  border-radius: 999px;
  background: conic-gradient(from 210deg,var(--rose),var(--gold),var(--teal),var(--lav),var(--rose));
  place-items: center;
}
.story-avatar b {
  display: grid;
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background: #fff;
  color: var(--ink);
  font-size: .82rem;
  font-weight: 850;
  letter-spacing: 0;
  place-items: center;
}
.story-meta { display: flex; min-width: 0; align-items: baseline; gap: .45rem; }
.story-name { font-size: .95rem; font-weight: 800; letter-spacing: 0; }
.story-time { color: rgba(17,20,28,.5); font-size: .82rem; }
.story-spacer { flex: 1; }
.story-icon {
  display: grid;
  width: 2.2rem;
  height: 2.2rem;
  flex: none;
  padding: 0;
  border: 0;
  border-radius: 999px;
  appearance: none;
  background: transparent;
  color: var(--ink);
  cursor: pointer;
  place-items: center;
}
.story-icon svg { width: 1.35rem; height: 1.35rem; }
.story-pause-pill {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 6;
  padding: .5rem 1rem;
  border-radius: 999px;
  background: rgba(17,20,28,.72);
  color: #fff;
  font-size: .82rem;
  font-weight: 700;
  letter-spacing: 0;
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%,-50%) scale(.85);
  transition: opacity 160ms ease, transform 160ms ease;
}
.story-screen.is-paused .story-pause-pill { opacity: 1; transform: translate(-50%,-50%) scale(1); }
.story-replay {
  position: absolute;
  bottom: max(1.2rem, calc(env(safe-area-inset-bottom) + .8rem));
  left: 50%;
  z-index: 6;
  padding: .7rem 1.2rem;
  border: 0;
  border-radius: 999px;
  background: var(--ink);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-size: .95rem;
  font-weight: 750;
  opacity: 0;
  pointer-events: none;
  transform: translateX(-50%) translateY(8px);
  transition: opacity 200ms ease, transform 200ms ease;
}
.story-screen.is-ended .story-replay { opacity: 1; pointer-events: auto; transform: translateX(-50%) translateY(0); }
.story-screen.bounce-left .story-deck { animation: story-bounce-left 240ms ease; }
.story-screen.bounce-right .story-deck { animation: story-bounce-right 240ms ease; }
@keyframes story-bounce-left { 30% { transform: translateX(2.2%); } }
@keyframes story-bounce-right { 30% { transform: translateX(-2.2%); } }
.utility {
  clear: both;
  width: fit-content;
  max-width: 100%;
  margin-top: 1.5rem;
  color: var(--muted);
  font-size: .78rem;
}
.utility summary {
  width: fit-content;
  cursor: pointer;
  list-style: none;
}
.utility summary::-webkit-details-marker { display: none; }
.utility summary::after { content: " +"; color: #8a94a3; }
.utility details[open] summary::after { content: " -"; }
.utility-panel {
  display: flex;
  gap: .5rem;
  align-items: flex-start;
  margin-top: .5rem;
}
.utility button {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  padding: .3rem .48rem;
  font: inherit;
}
.utility pre {
  max-width: min(72vw, 34rem);
  max-height: 12rem;
  overflow: auto;
  margin: 0;
  padding: .5rem;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: rgba(255,255,255,.62);
}
@media (min-width: 54.001rem) {
  #capsule-root[data-view-mode=present] .view-switcher { float: none; }
}
@media (prefers-reduced-motion: reduce) {
  .story.is-active .story-kicker,
  .story.is-active .story-headline,
  .story.is-active .story-body,
  .story.is-active .story-asset,
  .story-screen.bounce-left .story-deck,
  .story-screen.bounce-right .story-deck { animation: none; }
  .story-screen { transition: none; }
}
@media (min-width: 54.001rem) {
  #capsule-root[data-view-mode=scroll] .reader-view { display: block; }
  #capsule-root[data-view-mode=present] {
    width: 100%;
    max-width: none;
    min-height: 100dvh;
    margin: 0;
    padding: 0;
  }
  #capsule-root[data-view-mode=present] .view-switcher {
    position: fixed;
    top: .75rem;
    right: .75rem;
    z-index: 20;
    float: none;
    margin: 0;
  }
  #capsule-root[data-view-mode=present] .utility { display: none; }
  #capsule-root[data-view-mode=present] .slides-view {
    display: block;
    width: 100%;
    height: 100dvh;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #202532;
    scroll-snap-type: none;
  }
  #capsule-root[data-view-mode=present] .slide-track {
    display: flex;
    width: max-content;
    height: 100%;
    gap: 0;
    transform: translateX(calc(var(--slide-index) * -100vw));
    transition: transform 260ms cubic-bezier(.22,.61,.36,1);
  }
  #capsule-root[data-view-mode=present] .slide {
    width: 100vw;
    height: 100dvh;
    flex: 0 0 100vw;
    aspect-ratio: auto;
    border-radius: 0;
    box-shadow: none;
    padding: clamp(3rem, 7vw, 6rem);
  }
  #capsule-root[data-view-mode=present] .slide h3 {
    font-size: clamp(4rem, 8vw, 8rem);
  }
  #capsule-root[data-view-mode=present] .slide p {
    font-size: clamp(1.35rem, 2.2vw, 2.1rem);
  }
  #capsule-root[data-view-mode=present] .slide-controls {
    position: fixed;
    right: .75rem;
    bottom: .75rem;
    z-index: 20;
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    padding: .25rem;
    border: 1px solid rgba(17,24,39,.14);
    border-radius: 999px;
    background: rgba(255,255,255,.78);
    color: var(--ink);
    font-size: .78rem;
    font-weight: 800;
    backdrop-filter: blur(10px);
  }
  #capsule-root[data-view-mode=present] .slide-nav {
    width: 1.9rem;
    height: 1.9rem;
    border: 0;
    border-radius: 999px;
    background: transparent;
    color: inherit;
    cursor: pointer;
    font: inherit;
  }
  #capsule-root[data-view-mode=present] .slide-nav:hover,
  #capsule-root[data-view-mode=present] .slide-nav:focus-visible {
    background: var(--ink);
    color: #fff;
    outline: 0;
  }
  #capsule-root[data-view-mode=present] .slide-nav:disabled {
    color: rgba(17,24,39,.32);
    cursor: default;
  }
  #capsule-root[data-view-mode=present] .slide-nav:disabled:hover {
    background: transparent;
    color: rgba(17,24,39,.32);
  }
}
@media (max-width: 54rem) {
  html { scroll-behavior: smooth; scroll-snap-type: y mandatory; scroll-padding-top: 0; }
  main { padding: 1.25rem .75rem 3rem; }
  #capsule-root[data-view-mode=scroll] {
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0;
  }
  .view-switcher {
    position: fixed;
    top: max(.55rem, env(safe-area-inset-top));
    right: max(.55rem, env(safe-area-inset-right));
    z-index: 20;
    float: none;
    width: fit-content;
    margin: 0;
  }
  #capsule-root[data-view-mode=present] {
    width: 100%;
    max-width: none;
    min-height: 100dvh;
    margin: 0;
    padding: 0;
  }
  #capsule-root[data-view-mode=present] .view-switcher,
  #capsule-root[data-view-mode=present] .utility { display: none; }
  .reader-view, .slides-view { display: none !important; }
  #capsule-root[data-view-mode=scroll] .mobile-view { display: block; max-width: none; }
  #capsule-root[data-view-mode=feed] .feed-view { display: block; max-width: none; }
  #capsule-root[data-view-mode=present] .reel-view { display: block; }
  .desktop-label { display: none; }
  .mobile-label, .mobile-feed-option { display: inline; }
  .mobile-view {
    margin: 0;
  }
  .feed-view {
    margin: 0;
    padding: 4rem .75rem 1.5rem;
  }
  .feed-header {
    border-radius: 8px;
  }
  .feed-list {
    gap: .75rem;
  }
  .feed-card {
    min-height: 12rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .mobile-hero {
    min-height: 100dvh;
    padding: max(4rem, env(safe-area-inset-top)) 1.15rem max(1.4rem, env(safe-area-inset-bottom));
    border: 0;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    scroll-snap-align: start;
    scroll-snap-stop: always;
    scroll-margin-top: 0;
    transition: box-shadow 180ms ease, border-color 180ms ease;
  }
  .mobile-hero:target,
  .mobile-item:target {
    border-color: rgba(17,24,39,.42);
    box-shadow: 0 0 0 3px rgba(17,24,39,.08);
  }
  .mobile-scroll-track {
    gap: 0;
    margin-top: 0;
  }
  .mobile-item {
    min-height: 100dvh;
    grid-template-columns: 1fr;
    align-content: center;
    gap: 1.05rem;
    padding: max(4rem, env(safe-area-inset-top)) 1.15rem max(1.4rem, env(safe-area-inset-bottom));
    border: 0;
    border-radius: 0;
    scroll-snap-align: start;
    scroll-snap-stop: always;
    scroll-margin-top: 0;
    transition: box-shadow 180ms ease, border-color 180ms ease;
  }
  .mobile-item:nth-child(1) { background: linear-gradient(160deg,#fff,#eaf8f5); }
  .mobile-item:nth-child(2) { background: linear-gradient(160deg,#fff,#fff1cf); }
  .mobile-item:nth-child(3) { background: linear-gradient(160deg,#fff,#ecebff); }
  .mobile-item:nth-child(4) { background: linear-gradient(160deg,#fff,#ffe4eb); }
  .mobile-index {
    width: fit-content;
    padding: .28rem .46rem;
    border-radius: 999px;
    background: rgba(15,118,110,.1);
    line-height: 1;
  }
  .mobile-copy h3 {
    max-width: 10ch;
    margin-bottom: .65rem;
    font-size: clamp(2.35rem,12vw,4rem);
    line-height: .93;
  }
  .mobile-copy p {
    max-width: 21rem;
    font-size: clamp(1.05rem,4.6vw,1.32rem);
    line-height: 1.32;
  }
  .slide { grid-template-columns: 1fr; }
  .story-phone {
    width: 100%;
    height: 100dvh;
    min-height: 0;
    margin: 0;
    border-radius: 0;
  }
}
""".strip()


def render_runtime() -> str:
    return """
(function(){
  var data = JSON.parse(document.getElementById("capsule-data").textContent);
  var root = document.getElementById("capsule-root");
  var about = document.getElementById("about-data");
  var copy = document.querySelector('[data-capsule-action="copy_as_json"]');
  var modeButtons = Array.prototype.slice.call(document.querySelectorAll("[data-view-target]"));

  var storyPhone = document.querySelector(".story-phone");
  var storyScreen = document.querySelector(".story-screen");
  var storyDeck = document.getElementById("story-deck");
  var storyProgress = document.getElementById("story-progress");
  var stories = storyDeck ? Array.prototype.slice.call(storyDeck.querySelectorAll(".story")) : [];
  var storyPause = document.getElementById("story-pause");
  var storyClose = document.getElementById("story-close");
  var storyReplay = document.getElementById("story-replay");
  var slideDeck = document.getElementById("capsule-slides");
  var slides = slideDeck ? Array.prototype.slice.call(slideDeck.querySelectorAll(".slide")) : [];
  var slidePrev = document.getElementById("slide-prev");
  var slideNext = document.getElementById("slide-next");
  var slideStatus = document.getElementById("slide-status");
  var slideIndex = 0;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var storyDuration = 5000;
  var storyIndex = 0;
  var elapsed = 0;
  var last = 0;
  var paused = true;
  var ended = false;
  var raf = 0;
  var down = null;
  var holdTimer = 0;
  var isHolding = false;
  var isVerticalDrag = false;
  var blurredPaused = false;
  var fills = [];

  function setMode(mode){
    root.setAttribute("data-view-mode", mode);
    modeButtons.forEach(function(button){
      button.setAttribute("aria-pressed", String(button.getAttribute("data-view-target") === mode));
    });
    document.documentElement.classList.toggle("is-deck-mode", mode === "present" && window.matchMedia("(min-width: 54.001rem)").matches);
    syncSlides();
    if (isDesktopDeckVisible() && slideDeck) slideDeck.focus({ preventScroll: true });
    if (mode === "present" && window.matchMedia("(max-width: 54rem)").matches) startStory();
    else pauseStory(true);
  }

  function syncSlides(){
    if (!slideDeck || !slides.length) return;
    slideIndex = Math.max(0, Math.min(slideIndex, slides.length - 1));
    slideDeck.style.setProperty("--slide-index", String(slideIndex));
    if (slideStatus) slideStatus.textContent = (slideIndex + 1) + " / " + slides.length;
    if (slidePrev) slidePrev.disabled = slideIndex === 0;
    if (slideNext) slideNext.disabled = slideIndex === slides.length - 1;
  }

  function nextSlide(){
    if (!slides.length) return;
    slideIndex = Math.min(slideIndex + 1, slides.length - 1);
    syncSlides();
  }

  function previousSlide(){
    if (!slides.length) return;
    slideIndex = Math.max(slideIndex - 1, 0);
    syncSlides();
  }

  function isDesktopDeckVisible(){
    return root.getAttribute("data-view-mode") === "present" && window.matchMedia("(min-width: 54.001rem)").matches;
  }

  function alignMobileHash(){
    if (!location.hash || location.hash.indexOf("#mobile-") !== 0) return;
    var target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    setMode("scroll");
    function align(){
      var top = target.getBoundingClientRect().top + window.pageYOffset;
      window.scrollTo({ top: top, behavior: "auto" });
    }
    requestAnimationFrame(function(){
      align();
      window.setTimeout(align, 80);
    });
  }

  function isStoryVisible(){
    return root.getAttribute("data-view-mode") === "present" && window.matchMedia("(max-width: 54rem)").matches;
  }

  function initProgress(){
    if (!storyProgress || fills.length) return;
    fills = stories.map(function(){
      var span = document.createElement("span");
      var fill = document.createElement("i");
      span.appendChild(fill);
      storyProgress.appendChild(span);
      return fill;
    });
  }

  function setFill(i, fraction){
    if (fills[i]) fills[i].style.setProperty("--fill", fraction);
  }

  function paintBars(){
    fills.forEach(function(_, i){ setFill(i, i < storyIndex ? 1 : 0); });
  }

  function syncPauseIcon(){
    if (!storyPause) return;
    var playing = !paused && !ended;
    storyPause.setAttribute("aria-label", playing ? "Pause" : "Play");
    storyPause.innerHTML = playing
      ? '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5l13 7.5-13 7.5z"/></svg>';
  }

  function pauseStory(value){
    paused = value;
    last = 0;
    if (storyScreen) storyScreen.classList.toggle("is-paused", value && isStoryVisible() && !ended);
    syncPauseIcon();
  }

  function activateStory(nextIndex){
    if (!stories.length) return;
    var clamped = Math.max(0, Math.min(nextIndex, stories.length - 1));
    var changed = clamped !== storyIndex;
    storyIndex = clamped;
    elapsed = 0;
    last = 0;
    ended = false;
    if (storyScreen) storyScreen.classList.remove("is-paused", "is-ended");
    stories.forEach(function(story, i){
      var active = i === storyIndex;
      if (active && changed) {
        story.classList.remove("is-active");
        void story.offsetWidth;
      }
      story.classList.toggle("is-active", active);
    });
    paintBars();
    syncPauseIcon();
  }

  function finishStory(){
    ended = true;
    paused = true;
    setFill(stories.length - 1, 1);
    if (storyScreen) storyScreen.classList.add("is-ended");
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    syncPauseIcon();
  }

  function nextStory(){
    if (ended) return;
    if (storyIndex < stories.length - 1) activateStory(storyIndex + 1);
    else finishStory();
  }

  function bounce(side){
    if (reduceMotion || !storyScreen) return;
    var className = side === "left" ? "bounce-left" : "bounce-right";
    storyScreen.classList.remove(className);
    void storyScreen.offsetWidth;
    storyScreen.classList.add(className);
    window.setTimeout(function(){ storyScreen.classList.remove(className); }, 260);
  }

  function previousStory(){
    if (storyIndex > 0) activateStory(storyIndex - 1);
    else bounce("left");
  }

  function frame(now){
    raf = requestAnimationFrame(frame);
    if (paused || !isStoryVisible()) {
      last = now;
      return;
    }
    var delta = last ? now - last : 0;
    last = now;
    elapsed += delta;
    var fraction = Math.min(elapsed / storyDuration, 1);
    setFill(storyIndex, fraction);
    if (fraction >= 1) nextStory();
  }

  function startStory(){
    if (!stories.length) return;
    initProgress();
    if (ended) activateStory(0);
    paused = false;
    if (storyScreen) storyScreen.classList.remove("is-paused");
    syncPauseIcon();
    if (!raf) raf = requestAnimationFrame(frame);
  }

  function isControl(target){
    return target.closest("button, input, a, .story-header");
  }

  function resetDrag(){
    if (!storyScreen) return;
    storyScreen.classList.remove("is-dragging");
    storyScreen.style.setProperty("--dismiss-y", "0px");
    storyScreen.style.setProperty("--dismiss-scale", "1");
    storyScreen.style.borderRadius = "";
  }

  function closeStory(){
    activateStory(0);
    setMode(window.matchMedia("(max-width: 54rem)").matches ? "feed" : "scroll");
  }

  function onDown(event){
    if (!isStoryVisible() || isControl(event.target)) return;
    var point = event.touches ? event.touches[0] : event;
    down = { x: point.clientX, y: point.clientY };
    isHolding = false;
    isVerticalDrag = false;
    holdTimer = window.setTimeout(function(){
      isHolding = true;
      pauseStory(true);
    }, 200);
  }

  function onMove(event){
    if (!down || !storyScreen) return;
    var point = event.touches ? event.touches[0] : event;
    var deltaX = point.clientX - down.x;
    var deltaY = point.clientY - down.y;
    if (!isHolding && (Math.abs(deltaX) > 12 || Math.abs(deltaY) > 12)) window.clearTimeout(holdTimer);
    if (deltaY > 12 && Math.abs(deltaY) > Math.abs(deltaX)) {
      isVerticalDrag = true;
      if (!isHolding) pauseStory(true);
      var y = Math.max(0, deltaY);
      storyScreen.classList.add("is-dragging");
      storyScreen.style.setProperty("--dismiss-y", y + "px");
      storyScreen.style.setProperty("--dismiss-scale", String(Math.max(.86, 1 - y / 1400)));
      storyScreen.style.borderRadius = Math.min(28, y / 6) + "px";
    }
  }

  function onUp(event){
    if (!down) return;
    window.clearTimeout(holdTimer);
    var point = event.changedTouches ? event.changedTouches[0] : event;
    var deltaX = point.clientX - down.x;
    var deltaY = point.clientY - down.y;
    var wasHold = isHolding;
    var wasVerticalDrag = isVerticalDrag;
    down = null;
    isHolding = false;
    isVerticalDrag = false;
    if (wasVerticalDrag) {
      if (deltaY > 120) closeStory();
      else {
        resetDrag();
        pauseStory(false);
      }
      return;
    }
    if (wasHold) {
      pauseStory(false);
      return;
    }
    if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
      deltaX < 0 ? nextStory() : previousStory();
      return;
    }
    var rect = storyScreen.getBoundingClientRect();
    var relativeX = (point.clientX - rect.left) / rect.width;
    if (!ended) relativeX < .33 ? previousStory() : nextStory();
  }

  modeButtons.forEach(function(button){
    button.addEventListener("click", function(){
      setMode(button.getAttribute("data-view-target"));
    });
  });
  if (about) about.textContent = JSON.stringify(data, null, 2);
  if (copy) copy.addEventListener("click", function(){
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  });
  if (storyPause) storyPause.addEventListener("click", function(){
    if (ended) activateStory(0);
    pauseStory(!paused);
  });
  if (storyClose) storyClose.addEventListener("click", closeStory);
  if (storyReplay) storyReplay.addEventListener("click", function(){
    activateStory(0);
    pauseStory(false);
  });
  if (slidePrev) slidePrev.addEventListener("click", previousSlide);
  if (slideNext) slideNext.addEventListener("click", nextSlide);
  window.addEventListener("wheel", function(event){
    if (!isDesktopDeckVisible()) return;
    event.preventDefault();
    if (Math.abs(event.deltaX) + Math.abs(event.deltaY) < 24) return;
    if (event.deltaX > 0 || event.deltaY > 0) nextSlide();
    else previousSlide();
  }, { passive: false });
  if (storyScreen) {
    storyScreen.addEventListener("pointerdown", onDown);
    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", function(){
      if (down) {
        down = null;
        resetDrag();
        pauseStory(false);
      }
    });
  }
  window.addEventListener("keydown", function(event){
    if (isDesktopDeckVisible()) {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        previousSlide();
      } else if (event.key === "ArrowRight" || event.key === " " || event.key === "PageDown") {
        event.preventDefault();
        nextSlide();
      } else if (event.key === "PageUp") {
        event.preventDefault();
        previousSlide();
      } else if (event.key === "Home") {
        event.preventDefault();
        slideIndex = 0;
        syncSlides();
      } else if (event.key === "End") {
        event.preventDefault();
        slideIndex = slides.length - 1;
        syncSlides();
      } else if (event.key === "Escape") {
        event.preventDefault();
        setMode("scroll");
      }
      return;
    }
    if (!isStoryVisible()) return;
    if (event.key === "ArrowLeft") previousStory();
    else if (event.key === "ArrowRight") nextStory();
    else if (event.key === " ") {
      event.preventDefault();
      ended ? activateStory(0) : pauseStory(!paused);
    } else if (event.key === "Escape") closeStory();
  });
  document.addEventListener("visibilitychange", function(){
    if (document.hidden) {
      if (!paused && !ended) {
        blurredPaused = true;
        pauseStory(true);
      }
    } else if (blurredPaused) {
      blurredPaused = false;
      pauseStory(false);
    }
  });
  window.addEventListener("resize", function(){
    if (!isStoryVisible()) pauseStory(true);
  });
  window.addEventListener("hashchange", alignMobileHash);
  initProgress();
  syncSlides();
  activateStory(0);
  if (location.hash && location.hash.indexOf("#mobile-") === 0) alignMobileHash();
  else if (window.matchMedia("(max-width: 54rem)").matches) setMode("feed");
})();
""".strip()


def render_html(manifest: dict, data: dict, source: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>{e(source["title"])}</title>
<script id="capsule-manifest" type="application/json">{json.dumps(manifest, indent=2)}</script>
<script id="capsule-data" type="application/json">{json.dumps(data, indent=2)}</script>
<style id="capsule-style">{render_style()}</style>
</head>
<body>
{render_asset_defs()}
<main id="capsule-root" data-view-mode="scroll">
{render_view_switcher()}
{render_reader(source)}
{render_mobile(source)}
{render_mobile_feed(source)}
{render_slides(source)}
{render_reel(source)}
<section class="utility" aria-label="Capsule utilities">
  <details id="about">
    <summary>Data</summary>
    <div class="utility-panel">
      <button data-capsule-action="copy_as_json" type="button">Copy JSON</button>
      <pre id="about-data"></pre>
    </div>
  </details>
</section>
</main>
<script id="capsule-runtime">{render_runtime()}</script>
</body>
</html>
"""


def compile_source(source_path: Path, output_path: Path) -> dict:
    source = load_source(source_path)
    data = build_data(source)
    manifest = build_manifest(source)
    manifest["integrity"]["content_hash"] = compute_content_hash(manifest, data)
    html_text = render_html(manifest, data, source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    return {"output": str(output_path), "uuid": manifest["uuid"], "bytes": output_path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile the multi-view Capsule demo.")
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    result = compile_source(args.source, args.output)
    print(f"Compiled {result['output']}")
    print(f"  uuid: {result['uuid']}")
    print(f"  file size: {result['bytes']:,} bytes")


if __name__ == "__main__":
    main()
