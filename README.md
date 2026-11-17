# Anime Crossover MUGEN (web)

A browser fighting game built on the real IKEMEN GO engine, compiled to
WebAssembly. Play it live at
https://anime-crossover-mugen.vercel.app/

Current roster (v4): Goku, Vegeta, DIO, Jotaro, Gojo, Sukuna, Meliodas,
Escanor, Black Polnareff, Vanilla Ice. A slim four-character build
(Sukuna, Gojo, Meliodas, Escanor) is in progress.

## What is in this repo

- `site/` — the website: page, touch controls, the IKEMEN GO WebAssembly
  engine (`ikemen.wasm`), and the loader that reassembles the game data.
- `tools/repack.py` — packs the game data into the chunked `game.pak`
  parts the site loads (Vercel Hobby caps a single file at 100 MB).
- `tools/verify-site.js` — checks a built site.
- `final-spec.json` / `spec-final-v4.json` — the roster and stage spec for
  the live build.
- `VERIFICATION.md` — what was tested before the live build shipped.

## What is NOT in this repo

The game data itself — the community characters, stages and sounds
(`ikemen-fs/`, about 500 MB) — is not checked in. It is assembled from
the original community character archives and packed with
`tools/repack.py`. The characters belong to their original authors;
see `site/CREDITS.md` for the full list.

## Run it

Serve `site/` over HTTP and open `index.html`. The engine needs the
packed game data (`ikemen-fs/game.pak.part*`); without it the title
screen loads but no characters are available.

## Credits

Engine: IKEMEN GO / WebMUGEN by energyjp. Characters and stages are
community work by their original authors — full credits in
`site/CREDITS.md`. Fan project, not commercial.
