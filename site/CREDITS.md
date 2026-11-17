# Credits — Cursed Clash

A free fan fighting game. Not for sale, not affiliated with any rights holder.

## Engine

- **IKEMEN GO** — open-source fighting game engine by ikemen-engine,
  MIT License. https://github.com/ikemen-engine/Ikemen-GO
- **WebMUGEN 2.3** — IKEMEN GO compiled to WebAssembly for the browser,
  plus Mugen Studio 2.0, by energyjp (energyjp/ikemen-go-web, MIT).
  https://energyjp.itch.io/energy-webmugen
- This site ships the published WebMUGEN 2.3 build files as its base,
  rebranded for Ashar, with the game (not the Studio) as the landing page.
  The engine binary is bit-identical to the published build; see
  `ikemen.wasm.build.txt` for its build stamp
  (engine SHA-256 `85b284982ca3b76fd2d0a3f3fbddb66f17dc888bf310fe0f9e6c138b61a38023`,
  source commit `03d4ff235d30325fe19a528bec9a917b47955ba6`).

## Screenpack and bundled content

- Screenpack art: Elecbyte's M.U.G.E.N screenpack (CC BY / CC BY-NC —
  see `ScreenpackLicense.txt`). Engine licence: `License.txt`.
  Third-party notices: `THIRD-PARTY-NOTICES.txt`.

## Characters (fan-made community content)

| Character | Version | Author |
|---|---|---|
| Goku | Goku End ssj (Base / Kaioken / Super Saiyan Blue) | Mikel8888 |
| Vegeta | Vegeta JUS (Base / SSJ / SSJ2 / SSG / SSB / SSBE) | Shiruzato / Mythos |
| Dio | DIO (The World, time stop) | Warusaki3 |
| Jotaro | Jotaro Kujo (Star Platinum, time stop) | Warusaki3 |
| Gojo | Gojo Shinjuku / Gojo Manga (Full) | RyoumenS |
| Sukuna | WR-Sukuna (Ryomen Sukuna) | Witherower (AKA Kuro Aonix / dawsaw) |
| Meliodas | Meliodas (Base / Demon / Assault Mode) | Salah |
| Escanor | Escanor | Soulfire AKA Diogo M |

## Stages

| Stage | Author |
|---|---|
| GardenSandLand | MysticG & MatreroG |
| Pokémon Stadium | Cirio, edited by AVPboy6754 |
| KFM / Stage 0 / Stage 1 / Stage Z / Interactive Stage | Elecbyte / IKEMEN GO (bundled defaults) |

## Touch controls

On-screen D-pad + buttons added on the hosting page. They dispatch the
same keyboard events the engine already listens for — no engine changes.

All rights to the original characters belong to their respective owners
(Dragon Ball: Akira Toriyama / Toei; JoJo's Bizarre Adventure: Hirohiko
Araki; Jujutsu Kaisen: Gege Akutami; The Seven Deadly Sins: Nakaba
Suzuki; Pokémon: Nintendo / Game Freak). Characters and stages are
fan-made community content, used here in a free, non-commercial fan game,
exactly as the MUGEN community has done since 1999.

## Notes

- First load downloads the whole game (~430 MB including the engine);
  everything is cached by the browser afterwards.
- If a character is missing, it was left out on purpose — see README.md.
