# スプライトファイル リネーム レポート

## 概要

icons/v2/ の連番付きスプライトファイルを `data/v1/pokemons.json` のフォルム名に合わせてリネームした。

## 実行日

- 2026-03-07

## 作業内容

### 1. PNG → WebP 変換

| 項目 | 値 |
|---|---|
| 変換ファイル数 | 1326 |
| 変換前合計 | 18.55 MB |
| 変換後合計 | 5.74 MB |
| 圧縮率 | 69.1% 削減 |
| 品質 | lossy q90 |
| losslessフォールバック | 0件 |

### 2. 連番ファイルのリネーム

連番 (`_01`, `_02`, ...) で保存されていたフォルム違いのファイルを、JSONのキー名に合わせてリネームした。

| 項目 | 値 |
|---|---|
| リネーム完了 | 122件 |
| 衝突 | 0件 |

### 3. 不要な連番バリアントの削除

JSONにフォルム別エントリがなく、ベースファイル1枚で十分なポケモンの連番ファイルを削除した。

| 項目 | 値 |
|---|---|
| 削除ファイル数 | 54件 |

| ポケモン | 削除数 | 理由 |
|---|---|---|
| Furfrou | 9 | トリミングフォルム |
| Alcremie | 8 | フレーバーフォルム |
| Floette | 5 | 花の色違い |
| Flabebe | 4 | 花の色違い |
| Florges | 4 | 花の色違い |
| Deerling | 3 | 季節フォルム |
| Sawsbuck | 3 | 季節フォルム |
| Castform | 3 | 天候フォルム |
| Genesect | 4 | カセットフォルム |
| Squawkabilly | 3 | 色バリエーション |
| Koraidon | 1 | 不要なバリアント |
| Maushold | 1 | 不要なバリアント |
| Miraidon | 1 | 不要なバリアント |
| Xerneas | 1 | 不要なバリアント |
| Cramorant | 2 | 不要なバリアント |
| Magearna | 1 | 不要なバリアント |
| Zarude | 1 | 不要なバリアント |

### 4. メガ進化・ゲンシカイキのリネーム

連番をメガ進化の命名規則に変更した。

| 項目 | 値 |
|---|---|
| リネーム数 | 50件 |

| パターン | 旧名 | 新名 | 件数 |
|---|---|---|---|
| メガ進化 | `{Name}_01` | `{Name}-Mega` | 43 |
| メガXY | `Charizard_01/_02`, `Mewtwo_01/_02` | `-Mega-X` / `-Mega-Y` | 4 |
| ゲンシカイキ | `Groudon_01`, `Kyogre_01` | `-Primal` | 2 |
| メガ（特殊） | `Slowbro_02` | `Slowbro-Mega` | 1 |

### 5. その他フォルムのリネーム

| 旧ファイル名 | 新ファイル名 |
|---|---|
| Aegislash_01 | Aegislash-Blade |
| Burmy_01, _02 | Burmy-Sandy, Burmy-Trash |
| Eternatus_01 | Eternatus-Eternamax |
| Gastrodon_01 | Gastrodon-East |
| Gimmighoul_01 | Gimmighoul-Roaming |
| Keldeo_01 | Keldeo-Resolute |
| Necrozma_03 | Necrozma-Ultra |
| Zacian_01 | Zacian-Crowned |
| Zamazenta_01 | Zamazenta-Crowned |
| Zygarde_01 | Zygarde-Complete |
| Cherrim_01 | Cherrim-Sunshine |
| Eiscue_01 | Eiscue-Noice |
| Hoopa_01 | Hoopa-Unbound |
| Morpeko_01 | Morpeko-Hangry |
| Palafin_01 | Palafin-Hero |
| Shellos_01 | Shellos-East |
| Darmanitan_02 | Darmanitan-Zen |
| Darmanitan_03 | Darmanitan-Galar-Zen |

## リネーム一覧

| 旧ファイル名 | 新ファイル名 |
|---|---|
| Arcanine_01.webp | Arcanine-Hisui.webp |
| Arceus_01.webp ~ _17.webp | Arceus-Normal.webp ~ Arceus-Steel.webp |
| Articuno_01.webp | Articuno-Galar.webp |
| Avalugg_01.webp | Avalugg-Hisui.webp |
| Basculegion_01.webp | Basculegion-F.webp |
| Basculin_01.webp, _02.webp | Basculin-Blue-Striped.webp, Basculin-White-Striped.webp |
| Braviary_01.webp | Braviary-Hisui.webp |
| Calyrex_01.webp, _02.webp | Calyrex-Ice.webp, Calyrex-Shadow.webp |
| Corsola_01.webp | Corsola-Galar.webp |
| Darmanitan_01.webp | Darmanitan-Galar.webp |
| Darumaka_01.webp | Darumaka-Galar.webp |
| Decidueye_01.webp | Decidueye-Hisui.webp |
| Deoxys_01.webp ~ _03.webp | Deoxys-Attack.webp ~ Deoxys-Speed.webp |
| Dialga_01.webp | Dialga-Origin.webp |
| Diglett_01.webp | Diglett-Alola.webp |
| Dugtrio_01.webp | Dugtrio-Alola.webp |
| Electrode_01.webp | Electrode-Hisui.webp |
| Enamorus_01.webp | Enamorus-Therian.webp |
| Exeggutor_01.webp | Exeggutor-Alola.webp |
| Farfetch'd_01.webp | Farfetch'd-Galar.webp |
| Geodude_01.webp | Geodude-Alola.webp |
| Giratina_01.webp | Giratina-Origin.webp |
| Golem_01.webp | Golem-Alola.webp |
| Goodra_01.webp | Goodra-Hisui.webp |
| Gourgeist_01.webp ~ _03.webp | Gourgeist-Small.webp ~ Gourgeist-Super.webp |
| Graveler_01.webp | Graveler-Alola.webp |
| Grimer_01.webp | Grimer-Alola.webp |
| Growlithe_01.webp | Growlithe-Hisui.webp |
| Indeedee_01.webp | Indeedee-F.webp |
| Kyurem_01.webp, _02.webp | Kyurem-White.webp, Kyurem-Black.webp |
| Landorus_01.webp | Landorus-Therian.webp |
| Lilligant_01.webp | Lilligant-Hisui.webp |
| Linoone_01.webp | Linoone-Galar.webp |
| Lycanroc_01.webp, _02.webp | Lycanroc-Midnight.webp, Lycanroc-Dusk.webp |
| Marowak_01.webp | Marowak-Alola.webp |
| Meloetta_01.webp | Meloetta-Pirouette.webp |
| Meowstic_01.webp | Meowstic-F.webp |
| Meowth_01.webp, _02.webp | Meowth-Alola.webp, Meowth-Galar.webp |
| Moltres_01.webp | Moltres-Galar.webp |
| Mr.Mime_01.webp | Mr.Mime-Galar.webp |
| Muk_01.webp | Muk-Alola.webp |
| Necrozma_01.webp, _02.webp | Necrozma-Dusk-Mane.webp, Necrozma-Dawn-Wings.webp |
| Ninetales_01.webp | Ninetales-Alola.webp |
| Ogerpon_01.webp ~ _03.webp | Ogerpon-Wellspring.webp ~ Ogerpon-Cornerstone.webp |
| Oinkologne_01.webp | Oinkologne-F.webp |
| Oricorio_01.webp ~ _03.webp | Oricorio-Pom-Pom.webp ~ Oricorio-Sensu.webp |
| Palkia_01.webp | Palkia-Origin.webp |
| Persian_01.webp | Persian-Alola.webp |
| Ponyta_01.webp | Ponyta-Galar.webp |
| Pumpkaboo_01.webp ~ _03.webp | Pumpkaboo-Small.webp ~ Pumpkaboo-Super.webp |
| Qwilfish_01.webp | Qwilfish-Hisui.webp |
| Raichu_01.webp | Raichu-Alola.webp |
| Rapidash_01.webp | Rapidash-Galar.webp |
| Raticate_01.webp | Raticate-Alola.webp |
| Rattata_01.webp | Rattata-Alola.webp |
| Rotom_01.webp ~ _05.webp | Rotom-Heat.webp ~ Rotom-Mow.webp |
| Samurott_01.webp | Samurott-Hisui.webp |
| Sandshrew_01.webp | Sandshrew-Alola.webp |
| Sandslash_01.webp | Sandslash-Alola.webp |
| Shaymin_01.webp | Shaymin-Sky.webp |
| Sliggoo_01.webp | Sliggoo-Hisui.webp |
| Slowbro_01.webp | Slowbro-Galar.webp |
| Slowking_01.webp | Slowking-Galar.webp |
| Slowpoke_01.webp | Slowpoke-Galar.webp |
| Sneasel_01.webp | Sneasel-Hisui.webp |
| Stunfisk_01.webp | Stunfisk-Galar.webp |
| Tatsugiri_01.webp, _02.webp | Tatsugiri-Droopy.webp, Tatsugiri-Stretchy.webp |
| Tauros-Paldea-Combat_01.webp ~ _03.webp | Tauros-Paldea-Blaze.webp, Tauros-Paldea-Aqua.webp, Tauros.webp |
| Thundurus_01.webp | Thundurus-Therian.webp |
| Tornadus_01.webp | Tornadus-Therian.webp |
| Toxtricity_01.webp | Toxtricity-Low-Key.webp |
| Typhlosion_01.webp | Typhlosion-Hisui.webp |
| Ursaluna_01.webp | Ursaluna-Bloodmoon.webp |
| Voltorb_01.webp | Voltorb-Hisui.webp |
| Vulpix_01.webp | Vulpix-Alola.webp |
| Weezing_01.webp | Weezing-Galar.webp |
| Wormadam_01.webp, _02.webp | Wormadam-Sandy.webp, Wormadam-Trash.webp |
| Yamask_01.webp | Yamask-Galar.webp |
| Zapdos_01.webp | Zapdos-Galar.webp |
| Zigzagoon_01.webp | Zigzagoon-Galar.webp |
| Zoroark_01.webp | Zoroark-Hisui.webp |
| Zorua_01.webp | Zorua-Hisui.webp |

## 最終ファイル数

| 項目 | 値 |
|---|---|
| 総ファイル数 | 1217 |
| 連番のまま残存 | 0 |

## 使用スクリプト

- `scripts/convert_png_to_webp.py` - PNG → WebP 変換
- `scripts/rename_numbered_sprites.py` - 連番リネーム
