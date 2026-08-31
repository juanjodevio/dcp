import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const wwwRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const indexPath = join(wwwRoot, "index.html");
const stylesPath = join(wwwRoot, "styles.css");
const PRIMARY_CTA_HREF = 'href="https://github.com/juanjodevio/dcp"';

const REQUIRED = [
  "dcp",
  "dbt Core",
  "Elementary",
  "Docker Compose",
  "self-host",
  "https://github.com/juanjodevio/dcp",
] as const;

const BANNED = ["sign up", "pricing", "start free", "open app"] as const;

describe("landing copy contract", () => {
  it("has index.html", () => {
    expect(existsSync(indexPath)).toBe(true);
  });

  it("has styles.css linked from index", () => {
    expect(existsSync(stylesPath)).toBe(true);
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain("styles.css");
  });

  it("includes required copy", () => {
    const html = readFileSync(indexPath, "utf8");
    for (const needle of REQUIRED) {
      expect(html, `missing ${needle}`).toContain(needle);
    }
  });

  it("omits banned SaaS CTA phrases", () => {
    const html = readFileSync(indexPath, "utf8").toLowerCase();
    for (const banned of BANNED) {
      expect(html, `banned phrase present: ${banned}`).not.toContain(banned);
    }
  });

  it("has skip link and main landmark", () => {
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain('href="#main"');
    expect(html).toContain('id="main"');
  });

  it("uses the primary GitHub CTA href", () => {
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain(PRIMARY_CTA_HREF);
  });

  it("references existing image and font assets", () => {
    const html = readFileSync(indexPath, "utf8");
    const css = readFileSync(stylesPath, "utf8");
    const images = [...html.matchAll(/(?:src|srcset)="(img\/[^"]+)"/g)].map((m) => m[1]);
    const fonts = [...css.matchAll(/url\("([^"]+\.woff2)"\)/g)].map((m) => m[1]);
    expect(images.length).toBeGreaterThanOrEqual(1);
    expect(fonts).toHaveLength(2);
    for (const rel of [...images, ...fonts]) {
      expect(existsSync(join(wwwRoot, rel)), `missing ${rel}`).toBe(true);
    }
  });
});
