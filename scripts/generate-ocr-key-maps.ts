import { mkdir, readFile, writeFile } from "node:fs/promises";
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

type LanguageEntry = Partial<Record<LanguageCode, string>>;
type LanguageMapFile = Record<string, LanguageEntry>;
type SourceEntry = { ja?: string; en?: string };

const standardColumns: LanguageCode[] = [
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

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = resolve(repositoryRoot, "data/v1/language-maps");

const categories = [
  {
    output: "pokemons.json",
    source: "data/v1/pokemons.json",
    translations: "i18n/pokemon.csv",
    columns: standardColumns,
  },
  {
    output: "moves.json",
    source: "data/v1/moves.json",
    translations: "i18n/move.csv",
    columns: standardColumns,
  },
  {
    output: "items.json",
    source: "data/v1/items.json",
    translations: "i18n/item.csv",
    columns: standardColumns,
  },
  {
    output: "abilities.json",
    source: "data/v1/abilities.json",
    translations: "i18n/abilitiy.csv",
    columns: standardColumns,
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

function toLanguageEntry(row: string[], columns: readonly LanguageCode[]): LanguageEntry {
  const entry: LanguageEntry = {};
  columns.forEach((language, index) => {
    const value = row[index];
    if (value) entry[language] = value;
  });
  return entry;
}

async function generateCategory(category: (typeof categories)[number]): Promise<void> {
  const [sourceContent, csvContent] = await Promise.all([
    readFile(resolve(repositoryRoot, category.source), "utf8"),
    readFile(resolve(repositoryRoot, category.translations), "utf8"),
  ]);
  const source = JSON.parse(sourceContent) as Record<string, SourceEntry>;
  const [header, ...rows] = parseCsv(csvContent);
  if (header.join(",") !== category.columns.join(",")) {
    throw new Error(
      `${category.translations} has an unexpected header: ${header.join(",")}`,
    );
  }
  const translations = rows.map((row) =>
    toLanguageEntry(row, category.columns),
  );
  const byJapanese = new Map(translations.map((entry) => [entry.ja, entry]));
  const byEnglish = new Map(translations.map((entry) => [entry.en, entry]));
  const output: LanguageMapFile = {};

  for (const [key, sourceEntry] of Object.entries(source)) {
    const translation =
      (sourceEntry.en ? byEnglish.get(sourceEntry.en) : undefined) ??
      (sourceEntry.ja ? byJapanese.get(sourceEntry.ja) : undefined);
    const combined: LanguageEntry = {
      ...translation,
      ...(sourceEntry.ja ? { ja: sourceEntry.ja } : {}),
      ...(sourceEntry.en ? { en: sourceEntry.en } : {}),
    };
    output[key] = Object.fromEntries(
      standardColumns.flatMap((language) =>
        combined[language] ? [[language, combined[language]]] : [],
      ),
    );
  }

  const destination = resolve(outputDirectory, category.output);
  await writeFile(destination, `${JSON.stringify(output, null, 2)}\n`, "utf8");
  const complete = Object.values(output).filter((entry) =>
    standardColumns.every((language) => entry[language]),
  ).length;
  console.log(`${category.output}: ${Object.keys(output).length} entries (${complete} complete)`);
}

await mkdir(outputDirectory, { recursive: true });
await Promise.all(categories.map(generateCategory));
