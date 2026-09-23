# OASis — theoasisproject.eu, self-hosted

A complete rebuild of the OASis project website, moved off the Hostinger Website
Builder into plain files you control. Same 27 pages, same layout, same content,
same forms — but an edit is now one command instead of a session in the builder.

## What is here

```
site-data.json     all the content of all 27 pages (the single source of truth)
build.py           turns site-data.json into the static site
oasis              content CLI (see "Editing" below)
server.js          local server + form backend (zero dependencies)
site/              the generated website — this is what gets deployed
  assets/          134 images, logos and backgrounds, all local
  fonts/           Lato, Inter Tight, Rubik, Karla, self-hosted
  media/           the two video backgrounds
tools/             the scripts used to mirror the old site and verify this one
```

Nothing loads from an external service at runtime: no Hostinger, no Google Fonts,
no CDN. Copy `site/` anywhere and it works.

## Running it

```bash
node server.js          # http://localhost:4173
python3 build.py        # regenerate site/ after editing content
```

`server.js` serves the site and accepts form submissions. It needs nothing
installed — Node 18+ and that's it.

## Editing

All the text and images live in `site-data.json`. The `oasis` CLI is the fast path:

```bash
./oasis pages                          # every page and its URL
./oasis text home                      # every text block on the home page, with ids
./oasis find "01/09/2026"              # where a deadline appears across the site
./oasis replace "01/09/2026" "15/10/2026"
./oasis show z3Ijyw                    # the raw HTML of one block
./oasis set z3Ijyw newtext.html        # replace it
./oasis images home                    # image blocks and their files
./oasis image zZ55dK ~/Desktop/new.jpg # swap a photo
./oasis build                          # regenerate site/
```

Each write keeps the previous version as `site-data.json.bak`.

Changing a deadline is now:

```bash
./oasis replace "Deadline 01/09/2026" "Deadline 15/10/2026" && ./oasis build
```

### Bigger changes

- **Move or resize a block**: elements carry `desktop` and `mobile` boxes
  (`top`, `left`, `width`, `height`) in `site-data.json`. Edit the numbers, rebuild.
- **Add a new open call page**: copy an existing page entry in `pages`, give it a
  new id and `slug`, copy its blocks and elements under new ids, then add a
  `nav` entry (`isHidden: true` keeps it out of the menu, like the current calls).
- **Colours and type**: the `styles` object holds the global type scale, the two
  button styles and the fonts.

## Calls: ordering and the country filter

The archived calls are no longer a hand-placed grid. `build.py` pairs each photo
with the caption sitting on it, reads the country and the deadline straight out of
that caption, and renders a real responsive grid **sorted by deadline, newest
first**. Add a new archived call and it lands in the right place by itself — there
is nothing to reposition.

Above the grid sits a country filter, built from the calls themselves: each chip
shows a country and how many calls it has. Picking one also writes it into the URL
(`/calls-for-artists-oasis?country=Portugal`), so a filtered view can be linked or
shared, and opening that link restores the filter.

The country is whatever appears before "Application Deadline" in the caption
(`Machaon - Slovakia Application Deadline 22/06/2026`). Keep that shape and both
the sorting and the filter keep working; `COUNTRIES` in `build.py` holds the list
of names recognised outright.

## Readability

Text over photographs is handled by measurement, not by eye, and the photographs
themselves are never dimmed:

- **Call cards** — a caption sitting on a picture gets a soft plate behind the words
  only. The top of the photo stays at full brightness. Captions are detected
  automatically, so any new card is covered.

  A plate is only given to a real caption: the text has to sit on the picture's
  bottom edge and run at least 70% of its width. Numbers and labels placed inside
  an image — the 13 / 10 / 300+ figures on the home page, for instance — are part
  of the composition and already have the design's own translucent band behind
  them; plating each of them separately just litters the picture.
- **The header** floats over each page's first image. `tools/contrast.py` reads the
  real pixels where the menu sits and works out the smallest scrim that brings the
  links to a 4.5:1 contrast ratio. Over a flat light colour a dark bar would look
  wrong, so there the brand colour is deepened instead until it reads.
- **Everything else** is checked end to end: `tools/audit.mjs` renders every page,
  hides the text and photographs the background; `tools/audit.py` measures each text
  box against the pixels actually behind it and writes `contrast-fixes.json`, which
  `build.py` folds back into the next build.

```bash
node tools/audit.mjs && python3 tools/audit.py && python3 build.py
```

Twelve text boxes still sit below the WCAG threshold. All twelve are the site's own
brand pairings — white on the orange blocks, cream on the teal — inherited from the
original design, so they are reported rather than silently restyled. Say the word
and they get fixed too.

## Forms

The five forms (two contact, three newsletter) post to `POST /api/forms`.
Submissions are appended to `data/submissions.jsonl`. To also receive them by email:

```bash
export RESEND_API_KEY=re_xxx
export FORM_TO=info@theoasisproject.eu
node server.js
```

Without a key the submission is still stored and the visitor still sees the
success message — nothing is lost.

## Deploying

Live preview: **https://oasis-project-eu.netlify.app**

The site is published on Netlify from the pre-built `site/` folder. To ship a change:

```bash
./oasis replace "..." "..."      # or edit site-data.json
python3 build.py
npx netlify-cli deploy --dir=site --prod
```

The five forms run on Netlify Forms: no server, no database, and every submission
is emailed to info@theoasisproject.eu (six notification hooks, one per form) while
also staying in the dashboard under Forms. The free tier covers 100 submissions a
month.

Moving the domain across is a separate, reversible step: see **MIGRATION.md**, and
run `./verify-migration.sh` afterwards. The short version is that the project
mailbox stays on Hostinger and the nameservers never move, so email cannot break.

### Old notes

**Static host (Netlify, Cloudflare Pages, any web server)** — publish `site/`.
`netlify.toml` is already set up. URLs stay extensionless (`/about-us-oasis`),
exactly as on the old site, so inbound links and search rankings carry over.
Forms need the small server, or swap in the host's own form handling.

**Own server** — `node server.js` behind a reverse proxy gives you the site and
working forms in one process.

Before pointing the domain over, check `site/sitemap.xml` covers every page and
that `info@theoasisproject.eu` still receives submissions.

## Fidelity

Verified against the live site at 1440px with Playwright: 25 of the 27 pages match
the original block-for-block to the pixel. Two known differences:

- `/about-us-oasis` — the block holding the interactive map is 67px shorter
  (the old builder left extra blank space under the embedded map; the map itself
  is identical in size and position).
- `/tai-open-call` — 4px.

`/calls-for-artists-oasis` now differs on purpose: its archive is a sortable,
filterable grid rather than a fixed layout.

On mobile (390px) every page renders with no horizontal overflow; total page
heights run 2–4% taller than the original because text wraps slightly differently.

## One thing worth doing

`site/media/1722882-uhd_2560_1440_25fps.mp4` is a 65 MB 4K video used as the
background of the Mission section — inherited from the old site, where it was
streamed from Pexels. Re-encoding it to 1080p would cut it to a few MB and make
the home page markedly faster:

```bash
ffmpeg -i site/media/1722882-uhd_2560_1440_25fps.mp4 -vf scale=1920:-2 \
       -c:v libx264 -crf 28 -an site/media/mission-1080p.mp4
```

Then point the block's `background.video.videoSrc` at the new file and rebuild.
