# Capsule — Core

**Version: v0.3.0 · 2026-05-19**

The short spec. One page. Pasteable into an LLM prompt. The full spec is in [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md).

A **Capsule** is a versioned, self-contained HTML file for work, data, or information worth preserving. It is a *memory object* — human-readable, machine-readable, and provenance-bearing in one. It packages a bounded data snapshot, a machine-readable manifest, embedded UI logic, and structured export behavior into one shareable, archivable, re-loadable file. It's a profile of HTML — not a new file format. The same outer contract works for any domain (recipes, research notes, decisions, journal entries, LLM-extracted summaries, maps, logs); domain-specific content lives in the data block. The strongest claim the format makes is **multi-producer interop**: LLMs (Claude, ChatGPT, Gemini), deterministic compilers (Python/Node build scripts), and human authors all produce the same envelope shape.

> **Terminology note.** Claude's "artifacts," ChatGPT's "Canvas," and similar features are *working canvases* — editable, iterable, the live output that sits next to a chat. Capsules are what those become when sealed for preservation, sharing, and archival. Different roles, complementary tools: think of capsules as the seal step that comes after the canvas step.

> **Note for LLMs producing capsules:** Use a *thinking* or *extended-reasoning* mode if your platform has one — Claude's Extended Thinking, ChatGPT's Thinking variants, Gemini's deep-think. In practice these produce noticeably more careful capsules: better personal-use defaults, light and dark themes, working markdown exports, CSP headers, richer data structures. Standard modes still work but produce rougher capsules; if you're in standard mode, reread the rules below carefully before producing.

## The twelve rules

1. **One file.** The capsule is a single `.html` document. No companion folders, no sidecar files, no external assets.

2. **No network — the capsule boundary is definitional.** Zero `fetch`, `XHR`, CDN references, ES-module imports, or external CSS. Everything inlined. The capsule must work identically opened via `file://` and over `http://`. *The seal is not a restriction on what capsules can do — it's what makes capsules possible.* An artifact that fetches live data, calls an external service, or depends on network availability at runtime is a different category of artifact (web app, live dashboard, connected document) — not a degraded capsule. Without the seal, there's no floor, no archive, no durability, no "open this in ten years and it still works." See `spec/CAPSULE_SPEC.md` §1.5 for the conceptual treatment.

3. **Five required blocks**, with these exact IDs:
   - `<script id="capsule-manifest" type="application/json">` — the manifest
   - `<script id="capsule-data" type="application/json">` — the data snapshot
   - `<style id="capsule-style">` — all CSS
   - `<main id="capsule-root">` — the UI root
   - `<script id="capsule-runtime">` — all JavaScript

4. **Manifest has these required fields:** `spec_version`, `uuid` (v4 — the canonical identifier for the capsule), `capsule_version` (semver), `title`, `description`, `type`, `created_at` (ISO 8601 UTC), `generator` (`name` + `version` + `kind`), `source` (`origin` + `snapshot_type` + `snapshot_id` + `included_records`), `privacy` (`visibility` + `contains_private_data` + `redaction_applied` + `external_dependencies: false`), `capabilities` (array including `"about"` plus at least one export). **Optional fields:** `parents` (Capsule-to-Capsule provenance — see rule 13 below); `derived_from` (non-Capsule provenance — array of objects with required `type` + `title` and recommended `reference` URL/URN, `role`, plus optional `hash`, `date`; for compositions, datasets, chats, documents, photographs, surveys, and anything else that isn't a Capsule but informs the artifact. Added in spec v0.3.6; full shape in `spec/CAPSULE_SPEC.md` §11.2); `source.spec_received` (version string of this Core spec, e.g., `"v0.3.0 · 2026-05-19"`, taken from the version line at the top of this file — should match the `spec_version` you set above); and `source.prompt_received` (the verbatim prompt the user gave you). These let future readers correlate output with the Core version and prompt that produced it. **Deprecated fields** (still accepted in v0.3, planned for removal in v0.4): `capsule_id` (a human-readable slug — redundant with `title`, and not guaranteed unique); `artifact_id` and `artifact_version` (the v0.1 names superseded by `capsule_id`/`capsule_version`); `related` (was unused soft-association array — provenance now lives in `parents` and `derived_from`).

5. **Honest provenance.** `generator.kind` is one of `"compiler"`, `"llm"`, `"human"`, `"hybrid"`. If an LLM produced the HTML, set `kind: "llm"` and add `version: "<model-id>"`. If an LLM synthesized the data content (extracted from an article, summarized a transcript, etc.), add an optional `synthesis` block: `{ kind, model, human_reviewed }`. Don't claim to be the reference compiler.

6. **Read-only data.** The runtime must never modify the `capsule-data` block. User state (annotations, verdicts, selections, inputs) lives in JavaScript memory only and materializes only when the recipient triggers an export.

7. **Capabilities don't lie.** Every capability declared in the manifest must have a working implementation. Required minimum: `"about"` (a panel showing the manifest, usually a `<details>` block) plus at least one export — one of `copy_as_json`, `copy_as_markdown`, `download_json`, `download_capsule`, `print_to_pdf`, or `export_response`. **Core capabilities** are reserved single words (the list above plus `filter`, `sort`, `search`, `annotate`, `highlight`, `rank`, `group`, `compare`, `copy_as_csv`, `copy_as_prompt`, `download_csv`). The `download_capsule` capability adds an in-capsule "save as HTML" button that DOM-serializes the document and triggers a download — the recommended export path for hosted capsules whose recipients would otherwise reach for Chrome's broken Save Page As. **Domain capabilities** are open under a `<domain>.<action>` naming convention — e.g., `media.play_audio`, `map.zoom_to_layer`, `code.execute_snippet`. The dotted form signals "consumers don't have to know about this; domain-specific consumers will."

8. **Response export structure.** When the capsule supports `export_response`, the exported JSON must follow this shape:
   ```json
   {
     "response_schema_version": "0.1.0",
     "capsule_reference": {
       "uuid": "...", "capsule_version": "...", "snapshot_id": "..."
     },
     "response": {
       "type": "annotation | ranking | selection | decision | feedback | form_data | freeform | patch",
       "created_at": "<ISO 8601>",
       "payload": { ... }
     }
   }
   ```

9. **Accessibility baseline.** Semantic HTML, keyboard navigable, ARIA labels on iconic controls, `prefers-reduced-motion` respected, skip-to-content link, `<html lang="...">` set.

10. **Capsules cannot be unshared.** Treat redaction and audience decisions as final before sharing. There's no mechanism to retract a capsule a recipient has already received.

11. **Runtime JS string-literal rule.** In the `capsule-runtime` block, **any string that contains or could contain a newline must use a backtick template literal**, never a `"..."` or `'...'` regular string literal with a raw line break inside. A raw line terminator inside a regular string literal is a JavaScript `SyntaxError` and breaks the entire runtime silently — this is the single most common bug class in LLM-produced capsules. This is a mechanical rule with no exceptions: if a string could contain a newline (markdown exports, multi-line templates, joined arrays), use backticks.

    ```js
    // WRONG — a real newline character inside "..." is a SyntaxError:
    const md = lines.join("
    ");

    // RIGHT — backtick template literal, immune to this bug:
    const md = lines.join(`\n`);

    // ALSO RIGHT — the two-character escape sequence \n inside "...":
    const md = lines.join("\n");
    ```

    The distinction that matters: in the third example, `\n` is two characters (backslash + n) that the JS parser interprets as a newline. In the first example, the source file contains an actual newline byte inside the quotes, which is illegal. LLMs often get these confused when generating long outputs — using backticks everywhere eliminates the failure mode entirely.

12. **Render content in the HTML, not at runtime.** The `<main id="capsule-root">` body must already contain the full readable artifact when the file is opened — title, prose, embedded media (`<img src="data:...">`, `<audio src="data:...">`, `<video src="data:...">`), tables, lists, metadata. Runtime JavaScript may *enhance* the capsule (wire up export buttons, dynamic UI, copy-to-clipboard) but **must not be required** to produce the readable content. Capsules are archives, not apps; they must remain readable in environments that don't execute inline scripts — iOS Files / QuickLook previews, email client previews, screen readers, search indexers, archive viewers, and future browsers whose JS support has drifted from today's APIs.

    ```html
    WRONG — empty placeholders waiting for JS to render content:
    <main id="capsule-root">
      <h2 id="title"></h2>
      <figure id="photo-frame"></figure>
      <p id="caption"></p>
      <dl id="meta"></dl>
    </main>
    <script>
      // 200 lines of `el.textContent = data.title` etc.
    </script>

    RIGHT — content is already in the HTML; JS is optional polish:
    <main id="capsule-root">
      <h2>The actual title</h2>
      <figure>
        <img src="data:image/jpeg;base64,..." alt="...">
      </figure>
      <p>The actual caption.</p>
      <dl>
        <dt>Date</dt><dd>~1993</dd>
        <dt>Place</dt><dd>Campbell River, BC</dd>
      </dl>
    </main>
    <script>
      // ~50 lines: just button click handlers
    </script>
    ```

    Why this matters: a capsule whose `capsule-root` is mostly empty `<div id="...">` containers will render as a blank page in any environment that blocks or restricts JS. The format claims to be portable, archival, and durable across decades — that claim only holds if the rendered artifact lives in the HTML itself. Pre-render at build time; use JS only where JS is genuinely required (clipboard, downloads, print dialog, dynamic UI). If a capsule has no interactive features, it may have no runtime JS at all.

## Data block shape

The `capsule-data` block is free-form JSON — whatever the domain needs. Two patterns recur:

- **`records[]` array** when the content is a set of discrete items (decision options, claims, photos, table rows, ranked choices).
- **Single document with named sections** when the content is a synthesis of one topic (a summary, briefing, research note, glossary, reference document). Top-level keys are themes appropriate to the topic — `summary`, `key_takeaways`, `decision_matrix`, `risk_register`, `inflammation_explainer`, `quick_recommendations`, whatever the content calls for. The *shape* is "top-level object with thematic sections"; the specific keys are free.

Use whichever fits the actual content. LLMs producing synthesis capsules from conversations consistently reach for the single-document shape; that's the natural fit for "summarize this." LLMs producing decision-support or list-shaped artifacts reach for `records[]`. Both are first-class.

## Minimum manifest example

```json
{
  "spec_version": "0.3.0",
  "uuid": "00000000-0000-4000-8000-000000000000",
  "capsule_version": "1.0.0",
  "title": "Example Capsule",
  "description": "A minimum valid capsule.",
  "type": "reference",
  "created_at": "2026-05-18T00:00:00Z",
  "generator": { "name": "claude.ai", "version": "claude-opus-4-7", "kind": "llm" },
  "source": {
    "origin": "private_database",
    "snapshot_type": "portable_excerpt",
    "snapshot_id": "snapshot:example_001",
    "included_records": 1
  },
  "privacy": {
    "visibility": "shared",
    "contains_private_data": false,
    "redaction_applied": false,
    "external_dependencies": false
  },
  "capabilities": ["about", "copy_as_json"]
}
```

## Provenance: when this capsule was forked from earlier ones

If the user started this conversation by pasting one or more existing capsules — "let's continue this," "compare these two," "build on this one" — record each one as a parent in the manifest's optional `parents` array. The recipient (months later, possibly a different person) needs to know what the conversation built on.

Each parent is a `{ uuid, title }` pair. The UUID is the load-bearing pointer (machine-actionable, globally unique); the title is denormalized at fork-time as a human-readability hint so readers don't have to dereference the UUID to know what the parent was.

```json
"parents": [
  {
    "uuid": "a7c3e9f8-1234-4abc-9def-1234567890ab",
    "title": "TN Visa Briefing"
  }
]
```

Multiple parents are supported and meaningful — a capsule that compares two earlier capsules, or that merges a second capsule into the conversation partway through, records all of them. The order is *introduction order*: the parent that seeded the conversation comes first; parents added later append. Don't record parents the user didn't actually paste in — `parents` is hard provenance, not "thematically related work."

If the conversation didn't start from a capsule, omit `parents` entirely (don't include an empty array — absent and empty are equivalent, and absent is cleaner).

## How to ask an LLM to produce a capsule

> **Use the canonical name when you write your prompt.** The format is called **Capsule** (singular). The v0.1 name *"Artifact Capsule"* was renamed in v0.2 and only persists in this repo's naming-history notes; legacy field values (`artifact_id`, `artifact_version`) are still accepted under v0.2 compatibility, but new prompts and new content should use just "Capsule." Empirically — see [RESEARCH.md F25](RESEARCH.md) — the legacy term persists in stored user prompt templates and leaks into the `prompt_received` field of newly-produced capsules. Update your template once and the leak goes away.

A working prompt fragment:

> Produce a Capsule conforming to the rules below. The output should be a single `.html` file with no external dependencies, no network requests, and these five embedded blocks: `capsule-manifest`, `capsule-data`, `capsule-style`, `capsule-root`, `capsule-runtime`. Set `generator.kind` to `"llm"` and `generator.version` to your model ID. Include at minimum the `about` capability (a `<details>` panel showing the manifest) and `copy_as_json` (a button that copies the data block to the clipboard). Use semantic HTML, keyboard-accessible interactions, and `textContent` (never `innerHTML`) when rendering data values.
>
> Pay particular attention to two rules and two encoding pitfalls that empirically trip LLM producers up:
>
> - **Rule 12** (render content in the HTML, not at runtime) — the `capsule-root` body must already contain the full readable artifact when the file is opened. Don't write empty `<h2 id="title"></h2>` placeholders and fill them in JS; write `<h2>The actual title</h2>` directly. JS is for *enhancement* (export buttons, dynamic UI), not for producing the basic rendered content.
> - **Rule 11** (runtime JS string-literal rule) — for any multi-line string in your runtime JavaScript, use backtick template literals.
> - **Don't HTML-encode JSON inside `<script>` blocks.** `<script>` and `<style>` are raw-text elements in HTML5: entities are NOT decoded inside them. If you write `&quot;` inside `<script id="capsule-manifest" type="application/json">`, the browser reads it as six literal characters and `JSON.parse(textContent)` throws at runtime. Write raw JSON: `{"key": "value"}`, with real `"` characters. HTML entities belong inside `<pre>` blocks where you're displaying JSON for humans, not inside data blocks where the runtime parses them.
> - **`snapshot_id` must start with the literal prefix `snapshot:`.** This is a fixed namespace marker, not a content descriptor — same shape as `urn:uuid:`. Don't substitute `conversation:`, `chat:`, `record:`, or any other prefix even if it feels semantically truer; the slug *after* the colon is where you describe the content. Correct: `snapshot:vmsl-soccer-culture-2026-05-19`. Wrong: `conversation:vmsl-soccer-culture-2026-05-19`.
>
> ### Be thorough about real content
>
> Capsules are preserved records, not chat replies. The recipient may open this file in five years. Do not truncate real content for brevity or for the sake of looking concise.
>
> - If the conversation produced ten meaningful takeaways, include all ten — don't pick a "best five" to keep things short.
> - If the conversation referenced URLs, papers, documents, datasets, or official sources, capture them (see the next section for the recommended shape).
> - If the conversation had caveats, nuance, uncertainty, dead ends, or open questions, include those — they're often the most useful preservation later.
> - If the conversation involved an embedded image, screenshot, chart, or other media that's central to the meaning, embed it as a `data:` URI (the CSP already permits `img-src data:`).
>
> The format has a 20 MB hard cap (in the full spec, raised from 15 MB in v0.3.3, with a 15 MB soft warning for email-attachment compatibility) and typical capsules sit well under 1 MB. There is no penalty for thoroughness and a real cost to omission.
>
> **The one limit:** be thorough about content that *actually existed in the conversation*. Do not invent. The goal is faithful preservation, not embellishment.
>
> ### Capture sources and links
>
> When the conversation references external materials — URLs, papers, official documents, datasets, datasets — capture them in a structured `sources` array in the data block, not only inline in prose. A recommended shape (use whatever fields fit the content):
>
> ```json
> "sources": [
>   {
>     "label": "City of Vancouver — False Creek South leases on City land",
>     "url": "https://vancouver.ca/home-property-development/false-creek-south-leases-on-city-land.aspx",
>     "role": "primary_evidence",
>     "accessed_at": "2026-05-17",
>     "note": "Used for City ownership, leasehold structure, and LISL payment context."
>   }
> ]
> ```
>
> Roles that have been useful so far: `"primary_evidence"`, `"background"`, `"citation"`, `"policy_basis"`, `"data_source"`, `"counterargument"`. Inline prose mentions are still fine — but the structured array makes sources queryable across capsules and survives when the prose is later summarized further. Capture sources even when they came from your training data and not a tool call, as long as you can name them honestly.
>
> ### Embed a QR code for the UUID (if you have code execution)
>
> If you have Python or another code-execution environment available, generate a QR code encoding `urn:uuid:<uuid>` (the manifest's `uuid` in RFC 4122 URN form) and embed it as a `data:image/png;base64,...` URI inside the rendered capsule.
>
> **Place it at the top-right of the page, visible above the fold.** Not inside the about panel, not in the footer. The QR is the capsule's visible identity badge: scannable from a printed page, recognizable across capsules, anchored to the canonical UUID. Top-right placement works for both general capsules (where the badge sits next to or beside the title) and single-page printable layouts like briefings (where it lives in the header strip). Keep it small (around 80–96 px square on screen, ~1.5 cm in print).
>
> Suggested layout pattern:
>
> ```html
> <header style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
>   <div>
>     <h1>Capsule Title</h1>
>     <p class="lede">...</p>
>   </div>
>   <figure class="capsule-qr" style="margin:0;display:flex;flex-direction:column;align-items:center;gap:0.2rem;font:10px ui-monospace,monospace;color:#6b7280;">
>     <img src="{data_uri}" alt="QR code for capsule UUID {uuid}" style="width:88px;height:88px;image-rendering:pixelated;display:block;">
>     <figcaption>{uuid_short}</figcaption>
>   </figure>
> </header>
> ```
>
> A minimal Python recipe with the `qrcode` library:
>
> ```python
> import qrcode, io, base64
> qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
> qr.add_data(f"urn:uuid:{uuid}")
> qr.make(fit=True)
> img = qr.make_image(fill_color="black", back_color="white")
> buf = io.BytesIO(); img.save(buf, format="PNG")
> data_uri = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
> ```
>
> If you don't have code execution available, omit the QR. Tooling can add it at ingest time. Don't fake a QR by hand-drawing SVG or guessing the encoding — a wrong QR is worse than no QR.
>
> Here are the rules:
>
> [paste the twelve rules above]
>
> The data I want to put in the capsule is:
>
> [paste your data]

## What this short spec does NOT cover

For anything below, see [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md):

- Content hash protocol and integrity verification
- Asset embedding rules and size tiers
- Full response payload schemas (per response type)
- Security rules (CSP, runtime sanitization, import validation)
- Registry and import workflow
- Versioning semantics across spec evolution
- Related-work positioning (TiddlyWiki, RO-Crate, MHTML, etc.)
- The full set of artifact types and capabilities

The Core defines what makes a file recognizable as a capsule. The full spec defines what makes it trustworthy at protocol level. A capsule that follows the Core but skips the full spec's hashing/security details is still a capsule — just one with weaker verification properties.
