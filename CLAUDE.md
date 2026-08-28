# Mongbotics website

Plain HTML and CSS marketing site for **Mongbotics**, Thailand's first
decentralized robotics company. No framework, no bundler, no dependencies.
Deploys to GitHub Pages by uploading this folder.

---

## Hard rules

**1. No em dashes. Anywhere.** Not in copy, not in comments. Use a full stop, a
comma or a colon instead. Hyphens inside real words are fine (`on-chain`,
`last-mile`, `peer-to-peer`). `tools/build.py` prints an em dash check on every
run. It must say CLEAN.

**2. Never invent facts.** Every claim, number and product description comes
from the source files listed below. If something is not in them, ask. Do not
write plausible sounding marketing copy.

**3. Show options, do not guess.** When the user asks for a design or copy
change, build a temporary comparison page rendering three to six real variants
side by side, open it, and let them pick a letter or number. Describing options
in prose does not work. Delete the comparison page afterwards.

**4. Verify in the browser, not by assumption.** Take a screenshot. Measure with
JavaScript when it matters (heights, wrapping, overflow, whether an image was
upscaled). State what was actually checked.

---

## Where the content comes from

Nothing on this site is written from scratch. Sources, in the parent folder:

| File | What it holds |
|---|---|
| `tools/deck-sources.md` | **All 15 deck slides, decoded to text.** Read this first |
| `Mongbotics_Deck.pdf` | The original. Use `tools/read-deck.py` to regenerate the above |
| `Mongbotics_Project_Plan_OnePage.pdf` | The written proposal. Soul.md fields, the RWA token transfer rule |
| Durable site | `durable.com/b/mongbotics-v7u36b21/website`, the boss's approved design. Needs the user's login |
| `tools/tech-sources.md` | Line by line map of the Technology page copy back to its source |

Neither PDF has extractable text with standard tools. There is no `pdftotext`
and no `poppler`. Both were read by decompressing the PDF streams in Python and
decoding the font ToUnicode maps.

**The deck is already done.** `python3 tools/read-deck.py` writes
`tools/deck-sources.md` with all 15 slides verbatim. Read that instead of
guessing, and instead of re-deriving the extraction. The one-page plan has not
been decoded this way yet; `tools/tech-sources.md` holds what was pulled from
it by hand for the Technology page.

---

## Build

Pages are **generated**, not hand edited. Editing a `.html` file directly gets
overwritten on the next build.

```bash
python3 tools/build.py
```

One Python file holds the content and emits all seven pages, so the nav, footer
and shared blocks cannot drift apart. Output is plain readable HTML with no
build step needed to serve it.

Pages: `index`, `technology`, `mongbot`, `mongcore`, `mongmarket`, `about`.

**There is no Contact page.** It was deleted on 2026-08-27. Everything that
used to point at it now points at `about.html#contact`, the "Partner with
Mongbotics." block at the foot of About Us. If a contact route is ever needed
again, that anchor is the target, not a new page.

---

## Local preview

```bash
python3 tools/serve.py .
```

Then `http://localhost:8765`.

**Do not use `python3 -m http.server`.** It is single threaded, speaks HTTP/1.0
with no keep alive, and ignores Range requests. A `<video>` hangs it and takes
the whole page down. There is no video on the site right now, but this still
applies the moment one comes back. `tools/serve.py` adds threads,
HTTP/1.1 and 206 partial responses. GitHub Pages does all three natively, so
this is a local problem only.

### Cache, fixed 2026-08-27

This used to be the single most common false alarm on this site: `styles.css`
was linked without a query, Chrome guessed its own expiry, and correct CSS
edits looked like they had done nothing.

Two fixes, both in place now:

- `build.py` links `styles.css?v=<hash of the file>`. Change the CSS, run the
  build, and the URL changes with it. Works on GitHub Pages too.
- `serve.py` sends `Cache-Control: no-store` locally.

**So a plain reload is now enough.** If a style change still looks like it did
nothing, check that you ran `python3 tools/build.py` after editing the CSS.
The hash is stamped at build time, not at request time.

---

## House style

Set in `styles.css` at the top.

| Token | Value |
|---|---|
| `--ink` | `#08111d` headings and dark sections |
| `--blue` | `#1769ff` the only accent colour |
| `--muted` | `#586575` body copy |
| `--white` | `#f8fbff` page background |
| `--line` | `#cad5e2` hairline rules |
| tinted panel | `#eef4fb` |

- **Arial.** Not Space Grotesk. The Durable design used Space Grotesk and the
  user explicitly chose the original Arial house style over it.
- **Tight tracking on headings**, around `-.05em`. This is the signature.
- **Sharp corners.** No border radius except pill buttons in older sections.
- **Hairline rules and monospace labels** carry the structure.
- Big headline sizes use `clamp()` so they never overflow their column.

Durable's design tokens are reference only. The site does not use them.

---

## Images

Everything in `images/` is already optimised. Originals are in
`images-original/`, sources in the parent folder and `Proton Drive Download`.

- Optimise with `sips -s format jpeg -s formatOptions 72 -Z 1600 in --out out`
- **Check the source resolution first.** `sips -Z` upscales silently.
  `mongbot-mall.jpg` is a 585px source blown up to 1920 and looks soft at full
  width. Verify with `sips -g pixelWidth` on the original before using an image
  large.
- `page_hero(..., crop="low")` keeps the bottom of the frame instead of the
  top. The About robot stands low in its picture and the default crop took its
  wheels off. Check the subject survives the crop before assuming a hero is
  done.
- Do not crop images with labels at their edges. `Robot_Specs` has text at top
  and bottom that a fixed height crop removes.
- `mongbot-hero.jpg`, `about-hero.jpg` and `technology-hero.jpg` are all
  ChatGPT renders at 1672x941. That is under 1920, so they are served at native size and never
  resized up. They hold at typical laptop widths.
- Logo walls: size by **height**, not width. The partner logos have differing
  aspect ratios and equal widths made Friendly Robots' plate look short.

### Video

**There is no video on the site as of 2026-08-27.** `videos/banner.mp4` was on
the MongBot hero, then moved down to "Where it operates", then replaced with
`images/network.jpg`. The file is still in `videos/` and nothing references it.
`page_hero(..., video=...)` still works if one is ever wanted again.

Kept for whoever needs it next: the original clip was **HEVC**, which Chrome
and Firefox often refuse. It was transcoded with macOS `avconvert`. There is no
`ffmpeg` and no Homebrew on this machine, and `avconvert` has no bitrate
control, only `--duration` and size presets, which is why it was trimmed rather
than compressed. **Video will not autoplay in a Claude driven browser tab**:
Chrome never even requests the file and `readyState` stays 0. It plays fine in
a normal tab. Do not conclude video is broken from automation alone.

---

## Known open items

- **Partner logos are off the site as of 2026-08-27**, on the boss's
  instruction. The files are still in `images/partners/` and nothing links to
  them. This also retired the unconfirmed-partnership risk, at least for now.
- **The team section is off the About Us page as of 2026-08-27**, same
  instruction. The copy is not lost: it is deck slide 4, in
  `tools/deck-sources.md`, and the markup can be rebuilt from there.
- **The enquiries line was lost with the Contact page.** "Partnerships, early
  access, and press" and the "Request early access." call to action only ever
  existed there. About Us carries email and location only. Worth asking
  whether either should come back.
- **Do not use the Star Wars image.** `c3po_r2d2.jpg` is a copyrighted film
  still. Naming R2-D2 and C-3PO in text is fine and is already in the deck.
- **Contact page has no real phone number.** The footer says "Call" with no
  number behind it.
- `images/banner-poster.jpg` is only 960px wide. It is fine as the clip's poster
  frame, which is all it is used for now. Do not put it back on a full bleed
  hero: the MongBot hero uses `images/cta.jpg` at 1920px instead.
- Page weight dropped sharply on 2026-08-27 when the video came off. The
  3.4 MB `videos/banner.mp4` is still on disk but unreferenced.

---

## Working with this user

- They drive. Do the work, do not push lessons or unrequested next steps.
- Be brief. They will say what they want changed.
- When they say nothing changed, suspect the CSS cache first.
- They are not a developer. Explain in plain terms only when asked.
