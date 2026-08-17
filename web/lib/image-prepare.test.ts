import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  burnRedactionRects,
  downscaleDimensions,
  mapRectsToScale,
  normalizeRect,
  sniffImageMime,
} from "./image-prepare.ts";

const here = dirname(fileURLToPath(import.meta.url));

test("sniffImageMime recognizes PNG JPEG WEBP magic bytes", () => {
  const png = Uint8Array.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  assert.equal(sniffImageMime(png), "image/png");

  const jpeg = Uint8Array.from([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10]);
  assert.equal(sniffImageMime(jpeg), "image/jpeg");

  const webp = new Uint8Array(12);
  webp.set([0x52, 0x49, 0x46, 0x46], 0);
  webp.set([0x57, 0x45, 0x42, 0x50], 8);
  assert.equal(sniffImageMime(webp), "image/webp");

  assert.equal(sniffImageMime(Uint8Array.from([0x00, 0x01])), null);
});

test("downscaleDimensions caps the long edge at 1600", () => {
  assert.deepEqual(downscaleDimensions(800, 600), { width: 800, height: 600, scale: 1 });

  const wide = downscaleDimensions(3200, 1800);
  assert.equal(wide.width, 1600);
  assert.equal(wide.height, 900);
  assert.equal(wide.scale, 0.5);

  const tall = downscaleDimensions(900, 3200);
  assert.equal(tall.width, 450);
  assert.equal(tall.height, 1600);
});

test("normalizeRect drops zero-area and orders corners", () => {
  assert.equal(normalizeRect(10, 10, 10, 20), null);
  assert.deepEqual(normalizeRect(20, 30, 5, 10), { x: 5, y: 10, w: 15, h: 20 });
});

test("burnRedactionRects writes opaque black into the buffer — not an overlay", () => {
  const width = 8;
  const height = 8;
  const rgba = new Uint8ClampedArray(width * height * 4);
  for (let i = 0; i < rgba.length; i += 4) {
    rgba[i] = 200;
    rgba[i + 1] = 100;
    rgba[i + 2] = 50;
    rgba[i + 3] = 255;
  }

  burnRedactionRects(rgba, width, height, [{ x: 2, y: 3, w: 3, h: 2 }]);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4;
      const inside = x >= 2 && x < 5 && y >= 3 && y < 5;
      if (inside) {
        assert.equal(rgba[i], 0, `r at ${x},${y}`);
        assert.equal(rgba[i + 1], 0, `g at ${x},${y}`);
        assert.equal(rgba[i + 2], 0, `b at ${x},${y}`);
        assert.equal(rgba[i + 3], 255, `a at ${x},${y}`);
      } else {
        assert.equal(rgba[i], 200);
        assert.equal(rgba[i + 1], 100);
        assert.equal(rgba[i + 2], 50);
      }
    }
  }
});

test("mapRectsToScale applies downscale to redaction geometry", () => {
  assert.deepEqual(mapRectsToScale([{ x: 10, y: 20, w: 40, h: 60 }], 0.5), [
    { x: 5, y: 10, w: 20, h: 30 },
  ]);
});

test("fixture PNG magic matches sniffImageMime (bytes on disk, not extension)", () => {
  // Tiny 1x1 PNG generated for this assertion — keeps the test offline.
  const path = join(here, "fixtures", "1x1.png");
  const bytes = new Uint8Array(readFileSync(path));
  assert.equal(sniffImageMime(bytes), "image/png");
});
