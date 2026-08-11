import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

type LanguageCode =
  | "ja"
  | "en"
  | "fr"
  | "de"
  | "it"
  | "es"
  | "ko"
  | "zhCn"
  | "zhTw";

type SourceEntry = { ja?: string; en?: string };
type ApiName = { language: { name: string }; name: string };
type ApiResource = { names: ApiName[] };

const languages: LanguageCode[] = [
  "ja",
  "en",
  "fr",
  "de",
  "it",
  "es",
  "ko",
  "zhCn",
  "zhTw",
];

const apiLanguageToCode: Record<string, LanguageCode> = {
  "ja-hrkt": "ja",
  en: "en",
  fr: "fr",
  de: "de",
  it: "it",
  es: "es",
  ko: "ko",
  "zh-hans": "zhCn",
  "zh-hant": "zhTw",
};

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const apiRoot = "https://pokeapi.co/api/v2";
const concurrency = 12;

const categories = [
  {
    api: "item",
    source: "data/v1/items.json",
    csv: "i18n/item.csv",
  },
  {
    api: "ability",
    source: "data/v1/abilities.json",
    csv: "i18n/abilitiy.csv",
  },
] as const;

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

function toIdentifier(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[’']/g, "")
    .replace(/♀/g, "-f")
    .replace(/♂/g, "-m")
    .replace(/[^A-Za-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase();
}

function apiNamesToRow(resource: ApiResource): string[] {
  const values = new Map<LanguageCode, string>();
  for (const entry of resource.names) {
    const language = apiLanguageToCode[entry.language.name];
    if (language && entry.name) values.set(language, entry.name);
  }
  return languages.map((language) => values.get(language) ?? "");
}

async function fetchTranslation(
  api: string,
  key: string,
  entry: SourceEntry,
): Promise<{ key: string; row?: string[]; reason?: string }> {
  const names = [entry.en, key].filter((value): value is string => Boolean(value));
  const candidates = [
    ...new Set(
      names.flatMap((name) => [name, name.replace(/Feather$/i, "Wing")]).map(toIdentifier),
    ),
  ];
  for (const candidate of candidates) {
    const response = await fetch(`${apiRoot}/${api}/${candidate}/`);
    if (response.ok) {
      const row = apiNamesToRow((await response.json()) as ApiResource);
      if (entry.ja) row[0] = entry.ja;
      if (entry.en) row[1] = entry.en;
      return { key, row };
    }
    if (response.status !== 404) {
      return { key, reason: `HTTP ${response.status}` };
    }
  }
  return { key, reason: "not found" };
}

async function mapConcurrent<T, R>(
  values: T[],
  mapper: (value: T) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(values.length);
  let nextIndex = 0;
  await Promise.all(
    Array.from({ length: Math.min(concurrency, values.length) }, async () => {
      while (nextIndex < values.length) {
        const index = nextIndex;
        nextIndex += 1;
        results[index] = await mapper(values[index]);
      }
    }),
  );
  return results;
}

for (const category of categories) {
  const csvPath = resolve(repositoryRoot, category.csv);
  const [sourceContent, csvContent] = await Promise.all([
    readFile(resolve(repositoryRoot, category.source), "utf8"),
    readFile(csvPath, "utf8"),
  ]);
  const source = JSON.parse(sourceContent) as Record<string, SourceEntry>;
  const rows = parseCsv(csvContent);
  const header = rows[0];
  if (header.join(",") !== languages.join(",")) {
    throw new Error(`${category.csv} has an unexpected header`);
  }

  const translatedJapanese = new Set(rows.slice(1).map((row) => row[0]));
  const translatedEnglish = new Set(rows.slice(1).map((row) => row[1]));
  const missing = Object.entries(source).filter(
    ([, entry]) =>
      !translatedJapanese.has(entry.ja ?? "") && !translatedEnglish.has(entry.en ?? ""),
  );
  const fetched = await mapConcurrent(missing, ([key, entry]) =>
    fetchTranslation(category.api, key, entry),
  );
  const additions = fetched.flatMap((result) => (result.row ? [result.row] : []));
  const unresolved = fetched.filter((result) => !result.row);

  if (additions.length > 0) {
    await writeFile(csvPath, serializeCsv([...rows, ...additions]), "utf8");
  }
  console.log(
    `${category.api}: ${additions.length} added, ${unresolved.length} unresolved`,
  );
  for (const result of unresolved) {
    console.log(`  ${result.key}: ${result.reason}`);
  }
}
