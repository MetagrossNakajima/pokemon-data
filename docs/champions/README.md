# Champions M-C dex release

Masters are published through the existing `data/v1` workflow. The mobile app bundles these same files and fetches them only on an explicit update. `learnset.json` and `type-chart.json` extend the shared Pokémon, move, ability and type masters; there is no separate dex snapshot, manifest or data-version comparison. Validation runs before publication.

## Reproduction

Use the exact commits in `sources.json` for both upstream checkouts. Build Showdown (`npm ci && node build`), then from this repository:

```sh
python3 scripts/champions/generate.py /path/to/pokemon-showdown /path/to/champout 2026-11-08
python3 scripts/generate_union_types.py
python3 scripts/champions/validate-release.py
python3 scripts/champions/verify-game-data.py /path/to/pokemon-showdown /path/to/champout
python3 scripts/champions/verify-serebii.py /tmp/pokedex-serebii
```

`generate.py` compares against the pinned original master (77a3f3d), so regenerating does not lose the before/after audit. `sources.json` records upstream URLs, commits, date, regulation and explicit aliases. The same arguments and source commits reproduce the same JSON. Serebii's live HTML may change; the audit records each URL and page hash and caches HTML locally.

## Decisions and verification

- 1,269 existing/new form entries; 346 available in M-C. Presence in the sprite archive or text archive is never used for availability. Showdown's Champions formats and species restrictions decide availability; battle forms also require an available parent.
- Only Champions-specific learnsets are read. Form inheritance is resolved before export. Every unavailable entry gets an empty array. Every learned move must exist and be available. Ambiguous mappings fail generation, except the explicitly documented pre-existing Arceus/Arceus-Normal and Urshifu/Urshifu-Single-Strike aliases.
- All 346 available Pokémon match champout in stats, types, abilities and weight. All 515 available moves match its power, accuracy, maximum PP, type, category and contact flag (Struggle has no masterdata row). See `game-data-verification.json`.
- All 346 form learnsets match Serebii, including separate male/female and regional tables. Rotom's five exclusive attacks are parsed from its separate Special Moves table, never shared across forms. See `serebii-verification.json`.
- `Meowstic-Mega` retains the existing male key. `Meowstic-F-Mega` is added for the female's distinct learnset. Its menu icon uses the existing shared mega sprite in the app's explicit mapping.
- `WaveShield` remains the internal key. The incorrect English display name **Wave Shield** is corrected to **Aura Guard** (はどうのぼうご), verified in champout's `TOKUSEI_319`. The type calculator's existing key continues to work.
- `TypeNull` is the canonical key. Its existing display names and `TypeNull.webp` filename are preserved.
- `changes.json` lists every changed base statistic, type, ability, weight, move power/accuracy/PP/category/target/contact field and source. Protect changes from 10 to 5 base PP. Showdown applies the Champions base-PP cap of 20; game UI dumps/Serebii show maximum PP (Protect: 8), which must not replace the base-PP field.
- Event-only ability slot `S` is excluded. In particular, Greninja's old Battle Bond event ability is not in Champions: champout `personal.json` entry 0658000 lists Torrent/Torrent/Protean (67/67/168).
- Ability descriptions are unmodified champout `OriginalText` in Japanese/English. Move text follows `waza.json`'s explicit text-file and label references, including generic `ui_control` descriptions. Display tags are handled in the app, not rewritten in the master. Struggle has no game-description entry; its separately attributed English supplement comes from Showdown's move text. Other unavailable descriptions without game text remain empty and the app reports absence.
- The full Champions sprite archive is bundled by the mobile repo's `tool/bundle_pokedex.py`; no sprite availability inference occurs here.
