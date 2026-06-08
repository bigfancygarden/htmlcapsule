# Chat-Window Capsule Compiler Prompt

Status: experimental dogfood prompt.

Purpose: let a general chat-window LLM produce a complete standalone Capsule candidate without running the Python compiler. This is intentionally a prompt pack, not a replacement for the deterministic compiler or validator.

Use this when you want to test whether an LLM can act as a "compiler in the chat window" from source notes to a single `.html` Capsule. The expected workflow is:

1. Paste the compiler prompt into a chat model.
2. Provide source notes or structured content.
3. Save the returned HTML as a `.html` file.
4. Validate it with the reference validator.
5. Feed any validation failures back with the repair prompt.
6. If the only failure is the provisional integrity sentinel, repair it with `compiler/repair_integrity.py`.
7. Ingest the candidate into HTML Vault for dogfood review.

## Tool-Use Note

Some chat systems may use Python, JavaScript, or another hidden/ad hoc tool while producing the final `.html`. That is allowed for dogfood, but it changes the trust tier:

- **Pure chat-window output**: `generator.kind` should be `"llm"`.
- **LLM plus an ad hoc script**: `generator.kind` should be `"hybrid"`, and the manifest or source notes should honestly record that a non-canonical helper assembled the file.
- **Reference compiler output**: `generator.kind` should be `"compiler"` when the official compiler owns final assembly. If an official tool only repairs `integrity.content_hash`, keep the original `"llm"` or `"hybrid"` producer kind and treat the repaired hash as a stronger verification signal, not a new authorship claim.

Do not let each chat invent a permanent compiler. If a tool is available, the preferred path is Prompt C (source model only) followed by the reference compiler, integrity repair when needed, and validator:

```bash
python3 compiler/compile_multiview.py source.json -o capsule.html
python3 compiler/repair_integrity.py capsule.html -o capsule.repaired.html
python3 compiler/validate.py capsule.repaired.html
```

## Important Limitation

A chat model should not be treated as the final integrity authority. It can draft the envelope, manifest, data, CSS, runtime, and presentation views, but it is not reliable enough to compute a canonical `sha256` content hash.

For this experiment, instruct the model to include:

```json
"integrity": {
  "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "hash_scope": "data+manifest"
}
```

That all-zero hash is a deliberate sentinel. It keeps the field shape valid while making the candidate fail the actual content-hash verification until a deterministic compiler, validator repair tool, or Vault repair workflow computes the real hash. If you need a fully conforming Capsule on first export, use the deterministic compiler.

## Prompt A: Generate A Standalone Capsule Candidate

```txt
You are acting as an experimental HTML Capsule compiler.

Your task is to produce one complete standalone HTML Capsule candidate as a single HTML document.

Output rules:
- Output only the HTML document.
- Do not wrap the answer in Markdown fences.
- Do not include commentary before or after the HTML.
- The document must be self-contained and work offline.
- Do not use external scripts, stylesheets, fonts, images, iframes, forms, network calls, fetch, XMLHttpRequest, WebSocket, EventSource, dynamic import, or remote URLs.
- Do not require JavaScript for the primary meaning. The readable content must already exist inside `<main id="capsule-root">`.
- JavaScript may enhance navigation, export/copy, filtering, slides, story playback, or other local behavior.
- Treat runtime as enhancement, not source of truth.

Capsule envelope requirements:
- Use HTML5 doctype.
- Include `<script id="capsule-manifest" type="application/json">`.
- Include `<script id="capsule-data" type="application/json">`.
- Include `<style id="capsule-style">`.
- Include `<main id="capsule-root">`.
- Include `<script id="capsule-runtime">`.
- Include a CSP meta tag:
  `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'`

Manifest requirements:
- Target spec_version `"0.3.0"`.
- Include `capsule_version`.
- Include a UUIDv4 in `uuid`.
- Include `title`, `description`, `type`, `profile`, `created_at`, `generator`, `source`, `privacy`, `integrity`, and `capabilities`.
- `generator.kind` must be `"llm"` or `"hybrid"`.
- `generator.spec_provided` must be `true`.
- `generator.spec_version_used` must be `"0.3.0"`.
- `source.origin` should be `"ai_synthesis"` unless the user provided another source.
- `source.snapshot_type` should be `"synthesis"` unless another value is more accurate.
- `source.snapshot_id` must start with `"snapshot:"`.
- `source.included_records` must be an integer.
- `privacy.external_dependencies` must be `false`.
- Use this provisional integrity block exactly, because chat models cannot reliably compute canonical hashes:
  `"integrity": { "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "hash_scope": "data+manifest" }`

Presentation requirements:
- Include `presentations[]`.
- At minimum declare:
  - reader: `{ "id": "reader", "profile": "reader", "entry": "#capsule-root", "navigation": "scroll", "required": true }`
- If the content benefits from mobile cards, add:
  - mobile: `profile: "mobile"`, `entry: "#capsule-mobile"`, `navigation: "scroll"`, `required: true`
- If the content benefits from a feed, add:
  - mobile_feed: `profile: "mobile"`, `entry: "#capsule-mobile-feed"`, `navigation: "scroll"`, `required: true`
- If the content benefits from slides, add:
  - desktop_slides: `profile: "slides"`, `entry: "#capsule-slides"`, `navigation: "paged"`, `chrome: "capsule"`, `required: true`
- If the content benefits from an Instagram-style story/reel, add:
  - mobile_story: `profile: "reel"`, `entry: "#capsule-reel"`, `navigation: "sequence"`, `chrome: "capsule"`, `required: true`
- Every declared `entry` must resolve to an element id in the HTML.
- Do not invent undeclared view modes.

Content requirements:
- The reader/root view must be useful without JavaScript.
- Do not make the root a blank shell.
- Include title, summary, and the important sections or records directly in HTML.
- Use semantic HTML: headings, sections, articles, lists, tables, figures where appropriate.
- Escape user-provided content correctly. Never place untrusted text directly into script code.
- Keep CSS purposeful and mobile-safe.
- Avoid tiny tap targets. Use at least 44px tap targets for interactive controls.
- Do not use negative letter spacing.
- Do not use remote assets.

Runtime requirements:
- JavaScript must be local only.
- Runtime may switch declared views by setting attributes or classes.
- Runtime may implement copy/export buttons from the embedded data.
- Runtime may implement slides/story playback.
- Runtime must not call native APIs, network APIs, or external code.
- Runtime must not hide the only readable content behind JavaScript.

Suggested capabilities:
- Always include `"about"`.
- Include `"copy_as_json"` if you implement a copy JSON control.
- Include `"download_capsule"` only if you implement a DOM-serialization download button.
- Include `"print_to_pdf"` only if print styles or print behavior exist.

Now create the Capsule from this source material:

[PASTE SOURCE MATERIAL HERE]
```

## Prompt B: Repair Against Validator Output

```txt
You previously produced an experimental HTML Capsule candidate.

Repair it using the validator output below.

Rules:
- Output the full corrected HTML document only.
- Do not output a diff.
- Do not wrap in Markdown.
- Preserve the user's content and meaning.
- Preserve the fixed Capsule envelope.
- Do not introduce external resources or network APIs.
- Do not remove the no-JS readable root layer.
- If the only failure is the all-zero provisional integrity hash, keep the all-zero hash unless the user supplied a deterministic repaired hash.
- If a presentation fails, either fix the referenced entry or remove that presentation declaration.
- Do not add new capabilities unless the implementation marker actually exists in the HTML/runtime.

Validator output:

[PASTE VALIDATOR OUTPUT HERE]

Current candidate HTML:

[PASTE CURRENT HTML HERE]
```

## Prompt C: Source Model Only

Use this lower-risk mode when you want the LLM to do the creative/semantic part, then pass the result to the deterministic compiler.

```txt
You are preparing source JSON for the HTML Capsule multiview compiler.

Output only JSON.
Do not wrap in Markdown.
Do not output HTML.

Create a source model with:
- title
- description
- type
- audience
- sections: array of id/title/body
- presentation_model.cards: array of id/role/title/body/source_sections
- optional assets with ids and alt text
- optional story_behavior: "locked" if this is intended to be a full-screen mobile story

The content should support:
- reader view
- mobile view
- mobile feed view
- desktop slides
- mobile story/reel

Source material:

[PASTE SOURCE MATERIAL HERE]
```

## Evaluation Checklist

After generating a chat-window Capsule candidate, check:

- Does the file open offline?
- Does the reader/root view make sense with JavaScript disabled?
- Are declared presentations visible in HTML Vault?
- Does the story/slides chrome avoid double-host chrome?
- Are tap targets usable on iPhone?
- Does the validator only fail on the known provisional hash issue?
- Did the model accidentally add remote URLs, iframes, forms, external fonts, or network APIs?
- Did the model fabricate provenance or source references?
- Is the result good enough to preserve as a dogfood fixture?
