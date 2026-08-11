import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const sourceUrl =
  "https://bulbapedia.bulbagarden.net/wiki/Items_in_other_languages";
const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const csvPath = resolve(repositoryRoot, "i18n/item.csv");
const expectedHeader = ["ja", "en", "fr", "de", "it", "es", "ko", "zhCn", "zhTw"];

function parseCsv(content: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < content.length; index += 1) {
    const character = content[index];
    if (quoted) {
      if (character === '"' && content[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        quoted = false;
      } else {
        field += character;
      }
    } else if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      row.push(field.trim());
      field = "";
    } else if (character === "\n") {
      row.push(field.trim());
      if (row.some(Boolean)) rows.push(row);
      row = [];
      field = "";
    } else if (character !== "\r") {
      field += character;
    }
  }
  row.push(field.trim());
  if (row.some(Boolean)) rows.push(row);
  return rows;
}

function encodeCsvField(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

function serializeCsv(rows: string[][]): string {
  return `${rows.map((row) => row.map(encodeCsvField).join(",")).join("\n")}\n`;
}

function decodeHtml(value: string): string {
  const named: Record<string, string> = {
    amp: "&",
    apos: "'",
    gt: ">",
    lt: "<",
    nbsp: " ",
    quot: '"',
  };
  return value
    .replace(/<[^>]*>/g, "")
    .replace(/&#(x[\da-f]+|\d+);/gi, (_, code: string) =>
      String.fromCodePoint(
        code[0].toLowerCase() === "x"
          ? Number.parseInt(code.slice(1), 16)
          : Number.parseInt(code, 10),
      ),
    )
    .replace(/&([a-z]+);/gi, (entity, name: string) => named[name] ?? entity)
    .replace(/\s+/g, " ")
    .trim();
}

function parseBulbapediaRows(html: string): Map<string, string[]> {
  const translations = new Map<string, string[]>();
  for (const rowMatch of html.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)) {
    const cells = [...rowMatch[1].matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/gi)].map(
      (match) => decodeHtml(match[1]),
    );
    if (cells.length !== 12 || !cells[1] || !cells[2]) continue;
    const chinese = cells[10].split(/\s*\/\s*/, 2);
    translations.set(cells[1], [
      cells[2],
      cells[1],
      cells[4],
      cells[5],
      cells[6],
      cells[7],
      cells[8],
      chinese[1] ?? "",
      chinese[0] ?? "",
    ]);
  }
  return translations;
}

async function fetchMandarinNames(englishName: string): Promise<[string, string] | undefined> {
  const pageName = englishName.replaceAll(" ", "_");
  const response = await fetch(
    `https://bulbapedia.bulbagarden.net/wiki/${encodeURIComponent(pageName)}`,
    { headers: { "User-Agent": "pokemon-data language-map updater" } },
  );
  if (!response.ok) return undefined;
  const html = await response.text();
  const match = html.match(
    /title="Taiwan and mainland China">Mandarin<\/span>[\s\S]*?<\/td>\s*<td>([\s\S]*?)<\/td>/i,
  );
  if (!match) return undefined;
  const namesOnly = match[1].replace(/<i\b[\s\S]*$/i, "");
  const names = decodeHtml(namesOnly).split(/\s*\/\s*/, 2);
  return names.length === 2 ? [names[1], names[0]] : undefined;
}

const response = await fetch(sourceUrl, {
  headers: { "User-Agent": "pokemon-data language-map updater" },
});
if (!response.ok) throw new Error(`Bulbapedia returned HTTP ${response.status}`);

const [html, csvContent] = await Promise.all([response.text(), readFile(csvPath, "utf8")]);
const rows = parseCsv(csvContent);
if (rows[0].join(",") !== expectedHeader.join(",")) {
  throw new Error("i18n/item.csv has an unexpected header");
}

const translations = parseBulbapediaRows(html);
let updatedRows = 0;
let updatedFields = 0;
for (const row of rows.slice(1)) {
  const translation = translations.get(row[1]);
  if (!translation) continue;
  let changed = false;
  for (let index = 0; index < expectedHeader.length; index += 1) {
    if (!row[index] && translation[index]) {
      row[index] = translation[index];
      updatedFields += 1;
      changed = true;
    }
  }
  if (changed) updatedRows += 1;
}

let individualPageUpdates = 0;
const missingChinese = rows.slice(1).filter(
  (row) => translations.has(row[1]) && !row[7],
);
for (let index = 0; index < missingChinese.length; index += 4) {
  const batch = missingChinese.slice(index, index + 4);
  const results = await Promise.all(batch.map((row) => fetchMandarinNames(row[1])));
  results.forEach((names, resultIndex) => {
    if (!names) return;
    const row = batch[resultIndex];
    row[7] = names[0];
    if (!row[8]) row[8] = names[1];
    individualPageUpdates += 1;
  });
}

await writeFile(csvPath, serializeCsv(rows), "utf8");
console.log(
  `Bulbapedia: parsed ${translations.size} items, updated ${updatedRows} rows ` +
    `(${updatedFields} fields), completed Chinese from ${individualPageUpdates} item pages`,
);
