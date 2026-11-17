# Anime Crossover MUGEN — verification record

Live URL: https://anime-crossover-mugen-ocixwkyhv-undeadash1010.vercel.app/
Deployment: dpl_9Vm1kuBD5MQxNgnjYFvCcJHuoA5d (READY), project anime-crossover-mugen (prj_aqzrf1Q7CBFuUGk4uHcEScvPNds5), Vercel second account, ssoProtection null.

## Local verification (chunked build, http://localhost:8123)
Tool: ~/workspace/webmugen-build/verify/verify-chunked.js → report ~/workspace/webmugen-build/verify/final-chunked/report.json
- Title: PASS (IKEMEN GO title screen, canvas, boot "41 files.", Build ID 1b05a04e707d, no panics)
- Touch: PASS — 11 buttons, X dispatches down:KeyI/up:KeyI, D-pad right dispatches down:KeyD/up:KeyD
- dio-vs-jotaro: PASS — real fight, timer 99, The World + Dio vs Jotaro + Star Platinum, GardenSandLand
- goku-vs-vegeta: PASS — real fight, timer 99, both with aura effects, GardenSandLand
- meliodas-vs-escanor: PASS — real fight, timer 99, Meliodas transforming vs Escanor + Rhitta, Pokemon Stadium
- gojo-vs-sukuna: fight-start PROVEN separately — Gojo's long cinematic intro completes; at t=180s the fight is live (lifebars, timer 99, "Gojo Shinjuku" vs "DIO" in the retest; Sukuna vs Dio also proven). Screenshot: ~/workspace/webmugen-build/verify/final/gojo-vs-dio-t180s.png
- consoleErrors: [], exceptions: [], panics: []
- Chunked pak byte-identity: concat of the 9 parts sha256 = 466fb050ddb2... = the manifest stamp (identical to the tested single-pak blob).

## Live verification (Vercel URL, real browser)
Tool: ~/workspace/webmugen-build/verify/pw/verify-live-pw.js (Playwright + full Chromium + local CONNECT forwarder on 127.0.0.1:18080, needed because the VM egress proxy drops unauthenticated CONNECTs and Chromium cannot do preemptive proxy auth) → report ~/workspace/webmugen-build/verify/final-live-pw/report.json
- Title: PASS — live title screen renders (screenshot 00-title.png), canvas true, no panics
- Touch: PASS — buttons:11 seen:down:KeyI,up:KeyI,down:KeyD,up:KeyD
- dio-vs-jotaro: LOADED — canvas true, boot identical to local, panics [], exceptions []; screenshot NOT captured (Playwright screenshot timed out 120s twice; renderer saturated in software rendering — harness limit, not a game failure; the same fight renders locally with timer 99)
- gojo-vs-sukuna: PASS — screenshot shows Gojo's intro ("NAH, I'D WIN.") live on Pokemon Stadium
- goku-vs-vegeta: LOADED — canvas true, panics [], exceptions []; screenshot NOT captured (same harness timeout; the same fight renders locally with timer 99)
- meliodas-vs-escanor: PASS — screenshot shows a live fight, timer 99, Escanor + Rhitta vs Meliodas, Pokemon Stadium
- exceptions: []
- consoleErrors: 4x "Failed to load resource: 404 (Not Found)" — see below.

## The 4x 404 (live run) — RESOLVED
The 404 is /favicon.ico, confirmed by curl (live favicon.ico returns 404; all 6 page scripts, touch-controls.css, ikemen.wasm, manifest.json and all 9 pak parts return 200). The browser requests a favicon on each page load and the site ships no favicon file. Cosmetic console noise only; the game is unaffected. Not fixed in this build — adding one would need a redeploy plus a full re-verify for a cosmetic file, so it is left as a known minor item.

## Known limitations (not verified)
- Phone viewport / touch on a real phone — his phone is the final test, as always.
- Real-world first-load time on mobile data (~432 MB first download, cached after).
- Performance on his Mali GPU — headless tests run at ~1 FPS under SwiftShader software rendering; phone hardware rendering will be far faster, but heavy characters may still hitch.
- studio.html (Mod Studio) — ships in the site, untested; its shipped-roster read falls back to "own files only" because the manifest no longer has a single "pack" (chunked parts instead).
- Netplay / online modes — not tested.

## Size
First-load download ≈ 432 MB (pak 407.63 MB in 9 parts of ≤50 MB + ikemen.wasm 24 MB + ~2 MB page/js). Cached after the first load. The 50 MB chunking exists because Vercel Hobby caps a single uploaded file at 100 MB.

---

## v3 — Goku + Sukuna fix (2026-11-17, deployed 2026-11-17 ~07:35 UTC)

Ashar's complaint: "Did u fix Goku as well? His character design look bad also Sukuna as well get reviews and working good model before adding bruh u don't double check". This build answers it with live screenshots, not code inspection.

### What was wrong (proven by live screenshots)

- **Goku End SSJ (Mikel8888, 2015) — REPLACED.** Live shots `verify/goku-sukuna/b1-goku-vs-vegeta-t25.png` and `d1-goku-vs-vegeta-t55.png`: Goku renders with a **teal/cyan gi top + dark green pants** (orange boots only) — no orange anywhere. Cause in code: `pal.defaults = 1..6` are all SSBLUE / KAIOKEN palettes; **no classic orange-gi palette exists** in the character, so it could not be fixed in place. No MugenArchive rating found for this exact model; it appears in /v/ tournaments (braacket) but that is not a review.
- **Goku SSJ3 (ss3goku, Warusaki3, 2005) — REPLACED (slot dropped).** Live shots `verify/goku-sukuna/d3-ss3goku-vs-dio-t55.png` (pal4) and `d4-ss3goku-pal1-vs-dio-t55.png` (pal1): SSJ3 Goku renders **entirely green in every palette** — green SSJ3 hair, green gi, greenish skin. All six .act palettes are green-dominant (164-181 of 256 entries greenish). Also noticeably taller than chibi DIO (scale mismatch). No review evidence for this 2005 model; the praised "SSJ3 HD" on MugenDB/AK1 is Sankiti's, a different character.
- **Ryomen Sukuna (WR-Sukuna, Witherower, v1.00, released 2026-11-01) — KEPT.** Live shot `verify/goku-sukuna/f3-sukuna-vs-dio-t90.png`: pink spiky hair, face markings, bare chest with black curse markings, white baggy pants, barefoot, four arms (Heian form), correct colours; lifebar portrait is a good Sukuna face. Idle pose is stiff/arms-out — exactly what the author admitted in the README ("his animations aren't great, but hey, they get the job done"). No community reviews exist yet (v1.00 is 16 days old); **no alternative standalone MUGEN Sukuna exists anywhere searchable** (only inside Dark Night's 4.6-17 GB full-game packs). Replacing a working model just to look busy was refused.

### Replacement: Goku by Ismael Perez

- Source: `chars-dl/goku-ismael/` (128 MB, on disk already). `Goku.def`: name "Son Goku", mugenversion 1.1, author Ismael De Jesús Pérez. Palettes BASE / SSJ1 / SSGSS / SSRED / ultra / ultra completo. Transforms in .cmd/.cns: Kaioken, SSJ1, SSJ2, SSG, SSGSS, Ultra Instinct.
- Review evidence: MugenDB lists it (Kaioken, SSJ2, SSJGOD, SSJ BLUE, Ultra Instinct; Win Mugen / Mugen 1.0+); AK1 DBZ list ("new sprites of version super super hero all forms"); mugen-characters blog 2021-05-15 ("all transformations (Kaioken, SSJ2, SSJGOD, SSJ BLUE, Ultra Instinct), nice sprites and a cool damage counter"). MugenDB warning heeded: JUS Gokus and non-JUS Gokus are different sprite sizes — hence the scale fix below.
- **Scale fix (the one code tweak):** `chars-dl/goku-ismael/add004basic.reb1`, [Size] xscale/yscale `.7` -> **`.47`** (only those two lines changed; verified by diff vs backup). Ismael rendered ~1.58x Vegeta's height at .7; at .47 the live shot shows Goku ~215px vs Vegeta ~200px (ratio 1.075, canon 175cm vs 164cm = 1.067).
- **Transforms: code-verified only, NOT visually proven.** The p1pal param does not trigger transformations (they are state changes, not palette picks); the f2 pal2 test was inconclusive (caught at "ROUND 1" in base form). The base form is visually verified; SSJ1/SSG/SSB/UI transforms exist as .cmd/.cns states but were not screenshot mid-transformation. Stated honestly, not claimed.
- **SSJ3 form gap:** Ismael covers base/SSJ1/SSJ2/SSG/SSB/UI/Kaioken but NOT SSJ3, and the old SSJ3 slot is dropped. Future option: Sankiti HD SSJ3 (57.6 MB, AK1 file 31750) — would push first-load to ~609 MB, over budget, unless Ismael's 23 MB .snd is dropped via def surgery (risky, untested). Not added.

### v3 test proof (all on the final build, stamp da1685cda340, phone-landscape 2400x1080)

- Select screen: `verify/goku-sukuna/k2-select-ismael.png` — 10-cell flat grid, Ismael's big portrait (clean Goku, orange gi, black hair) renders correctly, name "Goku". `m2-after-2-right.png` — DIO big portrait renders. `m3-select-sukuna.png` — Gojo big portrait renders (cursor landed on cell 5, one short). `p2-select-sukuna.png` — Sukuna big portrait renders (pink hair, face markings, bare chest, "Ryomen Sukuna"). All via self-checking probe11 (pixel screen detector + screenshot-hash movement detection; probe8/9/10 failures documented in session notes: ArrowRight is not a P1 move key — WASD is; ~1 FPS swallows quick keypresses).
- Fights: `j1-ismael-scaled-vs-vegeta-t25.png` / `j1-ismael-scaled-vs-vegeta-t55.png` — scaled Ismael vs Vegeta, timer 99, zero panics/exceptions. `j2-ismael-scaled-vs-dio-t55.png` — Ismael vs DIO, ROUND 1 starting. `f3-sukuna-vs-dio-t90.png` — Sukuna full view, correct colours. Console errors in all probes: only the known cosmetic /favicon.ico 404s.
- SFF portrait audit (correct field offsets: group at +12): Ismael 9000,0/9000,1/9000,70 exist; Sukuna 9000,0/9000,1 exist; Vegeta 9000,0-8,91; DIO 9000,0-2.
- Regression note: DIO vs Jotaro was NOT re-run on the final build (probe5b killed before it ran). DIO/Jotaro files are byte-identical to v2 (repack validation + same content) and their v2 live fight passed; the only changed character is Goku. Stated as a gap, not claimed as tested.

### Deploy

- Vercel production deploy dpl_9iMmAHa3CaJXZWtomXCouh84Uvte (same project anime-crossover-mugen). Live: https://anime-crossover-mugen.vercel.app/ — HTTP 200, manifest stamp **da1685cda340** (cache-busted fetch; the bare manifest.json read showed the stale v2 stamp 3c7f21660d08 from CDN cache — verify with ?v=da1685cda340), all 11 parts 200.
- final-spec.json updated to the v3 spec. APK NOT rebuilt, Google Drive NOT touched (his order — he does not want to re-download; Drive file 1ACiUSJLGBUXwe5DHR1snSRk-raTIw5b9 still serves v2).

### Size

- First-load ≈ **551 MB** (pak 525.31 MB in 11 parts + ikemen.wasm 24 MB + ~2 MB page/js) — inside his 500-600 MB budget. Cached after first load.

### Remaining honest gaps

- Ismael's big portrait is slightly clipped at the bottom (lower gi cut by the panel edge); face, hair, shoulders and chest fully visible. Minor cosmetic, not a ship-blocker.
- Transforms not visually proven (see above). SSJ3 form has no slot (see above).
- Phone test on his real phone is still the final gate (first load ~551 MB on mobile data; Mali GPU performance untested). Headless tests run at ~1 FPS under SwiftShader.
- Netplay untested. studio.html untested.

## v4 — Sukuna swap: two-armed Shinjuku (2026-11-17, deployed 2026-11-17 ~08:20 UTC)

### What changed
- **Ryomen Sukuna (Heian, Witherower, 4 arms) REPLACED by Ryomen Sukuna (Shinjuku) by RyoumenS** (Nov 2024 release, same author as the Shinjuku Gojo already in the build). Ashar rejected the four-armed Heian form from the v3 screenshot ("two hands one"). Shinjuku = Megumi's body, two arms by canon.
- Source file: `chars-dl/Ryomen Sukuna (Shinjuku).rar` (59,957,995 bytes, SHA-256 e2f00e8345a3bc194811e4ca755585dd3a58d71eac42d3518b0f750bff541afe — MATCHED). Fetched via a third-party MediaFire downloader worker (mediafire-player.kuy.workers.dev /api/get) after MediaFire direct + cloud-browser downloads all failed from this VM.
- Extracted to `chars-dl/sukuna-shinjuku/` (flattened to the Gojo folder layout: def + files at top level). Old Heian folder `chars-dl/sukuna/` kept untouched as backup. Spec: `spec-final-v4.json` (also copied to `final-spec.json`); select_def line `sukuna/WR-Sukuna.def` -> `sukuna/Sukuna Manga (Full).def`; same select slot (cell 5).
- Audit: def name "Sukuna Manga (Full)", displayname "Sukuna Shinjuku", author RyoumenS, mugenversion 1.1. SFF v2, 1533 sprites; portraits 9000,0/9000,1 exist (parsed with the sffaudit.js layout: sprOfs at +36, sprNum at +40, 28-byte nodes, group at node+0). All [Files] entries present (ia.cns case pattern identical to the working Gojo — engine handles it). Extracted size 74 MB vs old Sukuna 95 MB.

### v4 test proof (final build, stamp ab3713a56586, phone-landscape 2400x1080, local server)
- Select screen: `verify/sukuna-v4/v4-select-sukuna.png` — cursor on cell 5, big portrait renders "Sukuna Shinjuku" (dark spiky hair, red eyes, face markings, red aura). All 5 right-moves hash-confirmed.
- Fight Sukuna vs Gojo (garden stage), probes `probe-sukuna-v4.js` + `probe-sukuna-v4b.js`: t25/t55/t90 frames pixel-identical (sampled pixels match) — Gojo's long cinematic intro was still playing (white beam effect, no HUD yet). t180: Gojo intro frame with "NAH, I'D WIN." speech bubble. **t240: ROUND 1, lifebars full, timer 99, "Sukuna Shinjuku" vs "Gojo Shinjuku" with correct portraits** — `verify/sukuna-v4/v4b-sukuna-vs-gojo-t240.png`. Sukuna renders with TWO arms, correct colours (black hair, face markings, white sleeveless top + hakama). Zero panics, zero exceptions in both probes; only the known cosmetic /favicon.ico 404s.
- Note for future probes: Gojo fights need ~240s wall-clock under SwiftShader before ROUND 1 appears; do not call a Gojo fight frozen before t240.

### Deploy
- Vercel production deploy dpl_EUqHmAyNP4iYfhodPFEncWDqV5LL (same project anime-crossover-mugen, deploy-files). Live: https://anime-crossover-mugen.vercel.app/ — HTTP 200, manifest stamp **ab3713a56586** (bare manifest.json fetch agrees this time — no stale CDN), all 11 pak parts 200, 386 files.
- APK NOT rebuilt, Google Drive NOT touched (his order; Drive file still serves v2).

### Size
- First-load ≈ **529 MB** (pak 503.46 MB in 11 parts + ikemen.wasm 24 MB + ~2 MB page/js) — inside his 500-600 MB budget (down from 551 MB in v3).

### Remaining honest gaps
- Sukuna's transforms/ultimates not visually proven (only base form + intro + ROUND 1 start). His phone test is still the final gate (first load ~529 MB on mobile data; Mali GPU performance untested). Netplay untested.

---

## v5 "Cursed Clash" — slim 4-character build (2026-11-17)

Live URL: https://anime-crossover-mugen.vercel.app/ (production domain)
Deployment: dpl_BdqC74gAiSQXdK8azEzpyn66sDSm (READY), same project
anime-crossover-mugen, Vercel second account. Manifest stamp **3faacd610059**
(verified by bare manifest.json fetch), 4 pak parts, 228 files, all parts
HTTP 200. The old v1 deployment URL stays frozen by design.

### Size — honest number: ~190 MB first load, NOT 100 MB
- Pak 165.62 MB (4 parts ≤ 50 MB, Vercel-safe) + ikemen.wasm 23.92 MB +
  page assets ~0.30 MB = **189.84 MB**. v4 was ~529 MB (2.79× smaller).
- Breakdown: characters 137.73 MB (Meliodas 63.05, Gojo 34.89, Sukuna 29.83,
  Escanor 9.96), stages 4.64 MB, data 20.78 MB (system.sff 14.52 MB).
- Cut: the other six characters, ~110 MB of `.snd` files, down to 2 stages
  (Garden + Stadium + 5 defaults), intro videos, `data/system.base.def`
  (engine verified booting without it).
- 100 MB is not reachable with these four characters intact: sprites alone
  are ~137.7 MB and the wasm is a fixed 23.9 MB, so the floor is ~162 MB
  before stages/data. Reaching ~100 MB would need dropping a character
  (Meliodas is the biggest at 63 MB) or re-encoding sprites.

### Roster (4)
Sukuna (Shinjuku, RyoumenS), Gojo (Shinjuku, RyoumenS), Meliodas (Salah),
Escanor (Soulfire). Deleted: Goku, Vegeta, DIO, Jotaro, Black Polnareff,
Vanilla Ice. No character sprites or portraits were touched.

### Name and title screen
**Cursed Clash** — no word "Mugen" anywhere visible. The one rendered
instance (F1 info box "Welcome to Energy's WebMUGEN!") now reads
"Welcome to Cursed Clash! (v5)"; the same word in the unused kfm motif was
also scrubbed. Remaining "mugen" strings are config keys (`mugenversion`)
and code comments, never rendered. Title background is the Arena fire image
with "CURSED CLASH" composited in the flame frame; menu moved to y=280 so
all 7 items (Arcade / VS Mode / Network / Practice / Mission / Watch Mode /
Options) are readable. Title and select backgrounds were swapped into
`system.sff` sprites (100,0) and (101,0) with the new reusable tool
`tools/sff-swap.py` (append-swap, verified by re-parsing and PNG-decoding
both sprites).

### Command list — 44 real moves
Taken from the four characters' own `.cmd` files; nothing invented.
Sukuna 14, Gojo 13, Meliodas 10, Escanor 7. Reachable from the MOVES button
(top-right) and the touch overlay's MOVES button. Tabs carry the AI-art
portrait thumbnails (`site/portraits/`); the engine's select portraits still
come from each character's SFF. The third-party zip's invented `.cmd` files
were NOT used (no `[State -1]`, invented command names).

### Touch buttons — labelled icons, same keys
D-pad (WASD) bottom-left. Right cluster: LIGHT / MED / HEAVY PUNCH (fist
icon, I/O/P), LIGHT / MED / HEAVY KICK (kick icon, K/L/;), CHARGE / START
(bolt icon, Enter — Start is every kept character's power-charge), PAUSE
(Escape), MOVES. Icons are the neon graphics from the zip's tiles
(`site/touch/icons/`). Keys unchanged.

### Tests (phone-landscape 2400×1080, local server port 8123)
Full probe `verify/v5/probe-v5.js` finished **PROBE V5 DONE**: title, select,
fight Meliodas vs Escanor t30–t150, MOVES panel open + Gojo tab. Zero panics.
Console noise only: favicon 404s (harmless, no favicon file) and "Go program
has already exited" (wasm runtime logging after page navigation/close).
Stadium stage verified in-engine (Meliodas vs Escanor, timer 99). Select
screen verified by a dedicated script (title → Arcade → Single Mode →
select, zero errors). Screenshots in `verify/v5/`: v5-00-title.png,
v5-01b-select.png, v5-02-fight-t30.png, v5-08-stadium-fight.png,
v5-03b-moves-gojo.png. His phone test remains the final gate.

### Known limitations
1. **PAUSE exits the game.** One Escape press during an active fight
   terminates the engine ("Engine exited"), confirmed twice. Pre-existing
   engine behaviour in this IKEMEN GO web build, not caused by v5 — the
   `[Pause Menu]` is defined in the motif but Escape never reaches it here.
   Tapping PAUSE mid-fight quits the game; a page reload restarts it.
2. **system.sff carries ~4.5 MB of orphaned sprite data** (old title/select
   backgrounds left behind by the two re-swaps). A compact would save it but
   risks breaking palettes, so it was left in.

### Deploy notes
- APK NOT rebuilt, Google Drive NOT touched (his order; Drive still serves
  the v2 APK).
- NOTE: the build tree's `final-spec.json` was still the v4 spec when this
  repo was refreshed — the repo's `final-spec.json` was set to the v5 spec
  content here so it describes the live build. The build tree's own
  `VERIFICATION.md` had no v5 section either; this section was added here
  from the v5 delivery report.

---

## v6 — Loading gate, PAUSE to top bar, FULLSCREEN, MOVES panel list visible (2026-11-17, deployed 2026-11-17 ~10:40 UTC)

### Why (his words, from his phone screenshot of the loading screen)
"Why is the moves and the fuckin pause there bruh add it somewhere else also add a full screen option as well and I meant moves showing list of moves he can do bruh". The screenshot showed the full touch cluster + the MOVES panel (tabs only, no list) on top of the "CURSED CLASH v5 — Downloading game data" loading box.

### What changed (website only; roster, name, size untouched)
1. **Loading screen is clean now.** `index.html` (+ `play.html`, same page): the game-only script adds `cc-loading` to `<html>` while the loading box is up and removes it (+ fires `cc-booted`) the moment the engine draws its first frames (`dropLoad()`; also removed in `leave()`). CSS hides `#tc-root`, `#tc-toggle`, `#cc-moves-btn`, `#cc-moves`, `#tc-pause-btn`, `#tc-fs-btn`, `#gomenu` under `html.cc-loading`. A tap on MOVES mid-load cannot open the panel visually (probe: panel display stays `none` even after its class toggles).
2. **PAUSE moved to the top bar.** `touch-controls.js`: the PAUSE entry is out of the fight cluster's util row (cluster keeps punch/kick + CHARGE/START + MOVES). New small text button `#tc-pause-btn` top-right (right: 126px), same Escape keydown/keyup as before — the engine behaviour (Escape quits mid-fight) is unchanged, only the button moved.
3. **FULLSCREEN button in the top bar.** `#tc-fs-btn` (right: 180px), Fullscreen API on `document.documentElement` (webkit fallback), toggles on second tap, refits the canvas on `fullscreenchange`. Verified entering + exiting in headless Chromium; Android Chrome supports the same API.
4. **MOVES panel shows the actual move list on a phone.** Root cause: the panel was `bottom: 170px` (clearing the touch cluster), leaving ~125 CSS px on a short landscape phone viewport — head + tabs ate it, the list hid below the fold. Now `bottom: 12px` (panel overlays the cluster while open, which is fine — the player is reading, not fighting) + a `max-height: 500px` tightening (smaller head/tabs/rows). Gojo: 13/13 rows visible, no scroll needed at 2400x1080. `moves-panel.js` also force-closes the panel on `cc-booted`, so a toggle fired during loading can never leave it open on the title screen (caught by the first v6 probe run: the panel appeared open on title with Sukuna's full list — which incidentally proved the list renders — then the force-close was added).
- Drive-by: `site/README.md` staleness fixed (was "~430 MB" + Goku/Vegeta as shipped; now ~190 MB, v5 cuts listed). `play.html` got the same loading-gate edits as `index.html`.

### v6 test proof (final build, phone-landscape 2400x1080, local server port 8123, probe `verify/v6/probe-v6.js`)
- Loading: `v6-00-loading.png` — only the CURSED CLASH v5 loading box (4.2/173.7 MB, 2%), nothing else on screen. State: `loadingClass: true`, goload VISIBLE, all seven controls hidden; tap on MOVES mid-load leaves panel display `none`.
- Title: `v6-01-title.png` — clean title, panel closed, top bar FULLSCREEN | PAUSE | MOVES | TOUCH, cluster without PAUSE. Fullscreen toggle: entered true, exited true.
- Moves: `v6-02-moves-gojo.png` — Gojo tab, SPECIAL MOVES (skill 1–8, junten ao, hanten aka) + SUPER MOVES (Clash, Muryokusho, Unlimited Hollow), 13/13 rows visible, panel height 1020px.
- Fight: `v6-03-fight.png` — Meliodas vs Escanor, timer 99, Garden; cluster is punch/kick + CHARGE/START + MOVES, PAUSE only in the top bar.
- Zero panics/exceptions; only the known cosmetic /favicon.ico 404.
- Probe notes: first run crashed on `playwright-core` not on the path (fixed with NODE_PATH to another project's node_modules) and on a variable shadowing bug (`fs`); the first full run caught the leftover-open panel, fixed with the `cc-booted` force-close, then re-run clean.

### Deploy
- Vercel production deploy **dpl_AMFTHvU3HgxTWHKQJk9UwDZeKRxY** (READY, same project anime-crossover-mugen, deploy-files; only 7 changed files uploaded, pak parts already on Vercel). Live: https://anime-crossover-mugen.vercel.app/ — HTTP 200, manifest stamp **3faacd610059** (unchanged — pak untouched), all 4 parts 200, 228 files. New code confirmed live (touch-controls.js has tc-fs-btn/tc-pause-btn, index.html has cc-loading, moves-panel.css has bottom: 12px). ssoProtection untouched (production serves the real page, no login).
- APK NOT rebuilt, Google Drive NOT touched.

### Size
- First-load unchanged ≈ **190 MB** (pak 165.62 MB in 4 parts + ikemen.wasm 23.92 MB + ~0.3 MB page/js). No character or size changes in this fix.

### Remaining honest gaps
- His phone test is still the final gate (loading-gate and fullscreen behaviour on his real moto g54 Chrome, first load on mobile data). Headless fullscreen entering/exiting is proven; the on-phone tap is not.
- PAUSE still quits the game mid-fight (pre-existing engine behaviour, Escape terminates the engine); only its button moved.
