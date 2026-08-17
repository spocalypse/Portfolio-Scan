/** Client-side SPEC §6.3 prepare: sniff, size guard, EXIF strip, downscale, burn redactions. */

export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
export const MAX_LONG_EDGE_PX = 1600;
/** Reject decoded bitmaps larger than this (width × height) before canvas work. */
export const MAX_DECODED_PIXELS = 40_000_000;
export const OUTPUT_MIME = "image/jpeg";
export const OUTPUT_QUALITY = 0.92;

export type RedactionRect = {
  /** Natural-image pixel space (pre-downscale). */
  x: number;
  y: number;
  w: number;
  h: number;
};

export type PrepareErrorCode =
  | "empty"
  | "too_large"
  | "unsupported_type"
  | "decode_failed"
  | "too_many_pixels"
  | "encode_failed";

export class PrepareError extends Error {
  readonly code: PrepareErrorCode;

  constructor(code: PrepareErrorCode, message: string) {
    super(message);
    this.name = "PrepareError";
    this.code = code;
  }
}

export function sniffImageMime(bytes: Uint8Array): "image/png" | "image/jpeg" | "image/webp" | null {
  if (bytes.length >= 8 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) {
    return "image/png";
  }
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) {
    return "image/jpeg";
  }
  if (
    bytes.length >= 12 &&
    bytes[0] === 0x52 &&
    bytes[1] === 0x49 &&
    bytes[2] === 0x46 &&
    bytes[3] === 0x46 &&
    bytes[8] === 0x57 &&
    bytes[9] === 0x45 &&
    bytes[10] === 0x42 &&
    bytes[11] === 0x50
  ) {
    return "image/webp";
  }
  return null;
}

export function downscaleDimensions(
  width: number,
  height: number,
  maxLongEdge: number = MAX_LONG_EDGE_PX,
): { width: number; height: number; scale: number } {
  const longEdge = Math.max(width, height);
  if (longEdge <= maxLongEdge) {
    return { width, height, scale: 1 };
  }
  const scale = maxLongEdge / longEdge;
  return {
    width: Math.max(1, Math.round(width * scale)),
    height: Math.max(1, Math.round(height * scale)),
    scale,
  };
}

/** Normalize drag order so w/h are positive; drop zero-area rects. */
export function normalizeRect(x0: number, y0: number, x1: number, y1: number): RedactionRect | null {
  const x = Math.min(x0, x1);
  const y = Math.min(y0, y1);
  const w = Math.abs(x1 - x0);
  const h = Math.abs(y1 - y0);
  if (w < 1 || h < 1) return null;
  return { x, y, w, h };
}

/**
 * Burn opaque black into an RGBA buffer. Rects are in the same pixel space as
 * `width`/`height` (call after mapping through downscale). Mutates `rgba` in place.
 * Acceptance for #10: covered samples are (0,0,0,255), not a UI overlay.
 */
export function burnRedactionRects(
  rgba: Uint8ClampedArray,
  width: number,
  height: number,
  rects: readonly RedactionRect[],
): void {
  if (rgba.length < width * height * 4) {
    throw new Error("RGBA buffer shorter than width*height*4");
  }
  for (const rect of rects) {
    const x0 = Math.max(0, Math.floor(rect.x));
    const y0 = Math.max(0, Math.floor(rect.y));
    const x1 = Math.min(width, Math.ceil(rect.x + rect.w));
    const y1 = Math.min(height, Math.ceil(rect.y + rect.h));
    for (let y = y0; y < y1; y++) {
      for (let x = x0; x < x1; x++) {
        const i = (y * width + x) * 4;
        rgba[i] = 0;
        rgba[i + 1] = 0;
        rgba[i + 2] = 0;
        rgba[i + 3] = 255;
      }
    }
  }
}

export function mapRectsToScale(rects: readonly RedactionRect[], scale: number): RedactionRect[] {
  if (scale === 1) return rects.map((r) => ({ ...r }));
  return rects.map((r) => ({
    x: r.x * scale,
    y: r.y * scale,
    w: r.w * scale,
    h: r.h * scale,
  }));
}

function userMessage(code: PrepareErrorCode): string {
  switch (code) {
    case "empty":
      return "Couldn't read that image — try a full-screen capture of the holdings list.";
    case "too_large":
      return "Image is too large (max 10 MB). Try a smaller capture.";
    case "unsupported_type":
      return "Choose an image file (PNG, JPEG, or WebP).";
    case "decode_failed":
      return "Couldn't read that image — try a full-screen capture of the holdings list.";
    case "too_many_pixels":
      return "Image resolution is too high. Try a screen capture instead of a raw camera photo.";
    case "encode_failed":
      return "Couldn't prepare that image — try again with a different capture.";
  }
}

function loadBitmap(blob: Blob): Promise<ImageBitmap> {
  return createImageBitmap(blob);
}

function canvasToJpegBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new PrepareError("encode_failed", userMessage("encode_failed")));
          return;
        }
        resolve(blob);
      },
      OUTPUT_MIME,
      OUTPUT_QUALITY,
    );
  });
}

/**
 * Validate bytes, decode, downscale, burn redactions, re-encode as JPEG.
 * Canvas re-encode drops EXIF. Redacted pixels are black in the output blob.
 */
export async function prepareScreenshot(
  file: File,
  redactions: readonly RedactionRect[] = [],
): Promise<File> {
  if (file.size <= 0) {
    throw new PrepareError("empty", userMessage("empty"));
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    throw new PrepareError("too_large", userMessage("too_large"));
  }

  const buffer = new Uint8Array(await file.arrayBuffer());
  const sniffed = sniffImageMime(buffer);
  if (!sniffed) {
    throw new PrepareError("unsupported_type", userMessage("unsupported_type"));
  }

  let bitmap: ImageBitmap;
  try {
    bitmap = await loadBitmap(new Blob([buffer], { type: sniffed }));
  } catch {
    throw new PrepareError("decode_failed", userMessage("decode_failed"));
  }

  try {
    const pixels = bitmap.width * bitmap.height;
    if (pixels > MAX_DECODED_PIXELS) {
      throw new PrepareError("too_many_pixels", userMessage("too_many_pixels"));
    }

    const { width, height, scale } = downscaleDimensions(bitmap.width, bitmap.height);
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) {
      throw new PrepareError("encode_failed", userMessage("encode_failed"));
    }

    ctx.drawImage(bitmap, 0, 0, width, height);

    if (redactions.length > 0) {
      const scaled = mapRectsToScale(redactions, scale);
      const imageData = ctx.getImageData(0, 0, width, height);
      burnRedactionRects(imageData.data, width, height, scaled);
      ctx.putImageData(imageData, 0, 0);
    }

    const blob = await canvasToJpegBlob(canvas);
    return new File([blob], "holdings-prepared.jpg", { type: OUTPUT_MIME, lastModified: Date.now() });
  } finally {
    bitmap.close();
  }
}
