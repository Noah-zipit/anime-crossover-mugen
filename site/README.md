# Anime Crossover MUGEN

A browser-playable anime crossover fighting game. Free, no install, no account.

- **Play:** open the site. Pick a fighter, pick a stage, fight.
  Keyboard: W/A/S/D to move, I/O/P for X/Y/Z, K/L/; for A/B/C, Enter for Start.
  Gamepads work too. On a phone, use the on-screen touch buttons.
  Add `?p1=dio/dio.def&p2=jotaro/jotaro.def` to the address to jump
  straight into a fight.
- **Roster (8):** Goku, Vegeta, Dio, Jotaro, Gojo, Sukuna, Meliodas, Escanor.
- **Stages:** GardenSandLand, Pokémon Stadium, plus the bundled defaults.
- **Modes:** Arcade, Versus, Team, Survival, Training, Watch.
  Online versus works peer-to-peer (copy-paste connect, no server).
- **Add characters:** open `studio.html` (Mod Studio), drop in MUGEN
  character folders, press Build & Play. Characters and stages are
  fan-made community content; keep it free and non-commercial.

## What this is built from

The published WebMUGEN 2.3 build by energyjp — the real IKEMEN GO engine
(MIT) compiled to WebAssembly — with the game as the landing page instead
of the Studio. Nothing about the engine was rewritten. See `CREDITS.md`.

## Not in this build (and why)

- **Mahoraga** — no free, working community character could be found.
- **Goku (Ismael Perez, incl. Ultra Instinct)** — found, but 128 MB for one
  character; the shipped Goku covers Base / Kaioken / Super Saiyan Blue.
- **Vegeta SSGSS (Blizzard)** — found, but Super Saiyan Blue only; the
  shipped Vegeta covers all six forms.
- **Gojo (WR-Gojo, Witherower)** — found, but 165 MB for one character;
  the shipped Gojo is the Shinjuku version.
- **City Metro stage, The Pit stage, SF2 Bison stage pack** — found, but
  not shipped (messy files / not anime-arena / oversized pack).

## Limits

- First load downloads the whole game (~430 MB including the engine);
  everything is cached by the browser afterwards.
- Desktop browser recommended (Chrome/Edge/Brave with hardware
  acceleration). Heavy characters can hitch; the browser build is
  single-threaded.
- Phone browsers: touch controls are built in, but a phone run is still
  the final test — it has not been verified on a real phone yet.
