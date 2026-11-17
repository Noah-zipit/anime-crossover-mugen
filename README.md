# Cursed Clash (v5)

A browser fighting game built on the real IKEMEN GO engine, compiled to
WebAssembly. Play it live at
https://anime-crossover-mugen.vercel.app/

Current roster (v5): **Sukuna (Shinjuku), Gojo (Shinjuku), Meliodas,
Escanor** — four characters, slimmed from ten. First load is **~190 MB**
(pak 165.62 MB + engine 23.92 MB); 100 MB was not reachable with these four
characters intact (sprites alone are ~137.7 MB, the engine is a fixed
~24 MB). The game is called **Cursed Clash** — no "Mugen" in the name
anywhere visible.

## What is in this repo

- `site/` — the website: page, labelled touch controls, the command-list
  panel (44 real moves from the characters' own `.cmd` files), the IKEMEN GO
  WebAssembly engine (`ikemen.wasm`), and the loader that reassembles the
  game data.
- `tools/repack.py` — packs the game data into the chunked `game.pak`
  parts the site loads (Vercel Hobby caps a single file at 100 MB).
- `tools/verify-site.js` — checks a built site.
- `tools/sff-swap.py` — swaps sprites into `system.sff` (used for the
  title and select backgrounds).
- `tools/v5-lite-assets.py` — prepares the v5 lite assets (portraits,
  touch icons, slot removal).
- `final-spec.json` / `spec-final-v5.json` — the roster and stage spec for
  the live build.
- `spec-final-v4.json` — the previous (10-character) build's spec, kept
  for reference.
- `VERIFICATION.md` — what was tested before each live build shipped,
  including the honest size numbers and known limitations.

## What is NOT in this repo

The game data itself — the community characters, stages and sounds
(`ikemen-fs/`, about 166 MB for v5) — is not checked in. It is assembled
from the original community character archives and packed with
`tools/repack.py`. The characters belong to their original authors;
see `site/CREDITS.md` for the full list.

## Run it

Serve `site/` over HTTP and open `index.html`. The engine needs the
packed game data (`ikemen-fs/game.pak.part*`); without it the title
screen loads but no characters are available.

## Known limitation

The PAUSE button (Escape) quits the game mid-fight instead of pausing —
pre-existing engine behaviour in this web build. A page reload restarts it.

## Credits

Engine: IKEMEN GO / WebMUGEN by energyjp. Characters and stages are
community work by their original authors — full credits in
`site/CREDITS.md`. Fan project, not commercial.
