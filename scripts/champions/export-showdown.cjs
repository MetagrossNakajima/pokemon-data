// Run after `npm ci && node build` in the pinned Showdown checkout.
const path = require('node:path');
const root = path.resolve(process.argv[2]);
const {Dex} = require(path.join(root, 'dist/sim/dex.js'));
const dex = Dex.mod('champions');
const {Learnsets} = require(path.join(root, 'dist/data/mods/champions/learnsets.js'));
const species = Object.fromEntries(dex.species.all().map(p => [p.id, p]));
// Cosmetic forms have distinct application keys but inherit the explicitly named parent.
for (const p of dex.species.all()) for (const name of p.cosmeticFormes || []) {
  const form = dex.species.get(name); species[form.id] = form;
}
console.log(JSON.stringify({species, moves: Object.fromEntries(dex.moves.all().map(m=>[m.id,m])), abilities: Object.fromEntries(dex.abilities.all().map(a=>[a.id,a])), learnsets: Learnsets, moveText: require(path.join(root, 'dist/data/text/moves.js')).MovesText, typeChart: dex.data.TypeChart}));
