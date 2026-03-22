#!/usr/bin/env python3
"""
generate_noisy_variants.py

Create noisy image/PDF variants from existing invoice files for testing
invoice extraction robustness (e.g. Python pipeline or future Power Platform flows).

What it does
------------
- Reads source invoice PDFs and/or images from an input directory
- Creates image-based noisy variants:
  - rotation
  - blur
  - reduced contrast
  - JPEG compression artifacts
  - optional grayscale
- Saves PNG/JPG outputs into a target folder
- Writes a CSV manifest describing each generated noisy file

Recommended usage
-----------------
1. First generate clean invoices with generate_invoices.py
2. Then run this script against that folder
3. Use the resulting noisy files for Day 2 test scenarios

Dependencies
------------
- pdf2image
- pillow

Optional system dependency for PDF input:
- poppler (required by pdf2image on many systems)

Install Python deps:
    pip install pillow pdf2image

Examples
--------
Create 8 noisy variants from generated PDFs:
    python generate_noisy_variants.py

Create 20 variants from a custom folder:
    python generate_noisy_variants.py --input-dir ./data/generated_invoices --count 20

If PDF conversion fails, convert a few invoices to PNG first and point the script
at an image folder instead.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except Exception:
    PDF_SUPPORT = False


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
PDF_EXTENSIONS = {".pdf"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate noisy variants of invoice files.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/generated_invoices"),
        help="Folder containing source invoice PDFs/images. Default: data/generated_invoices",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/noisy_variants"),
        help="Folder to write noisy variants. Default: data/noisy_variants",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path("data/expected_outputs/noisy_variants_manifest.csv"),
        help="CSV manifest output path. Default: data/expected_outputs/noisy_variants_manifest.csv",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=8,
        help="Number of noisy variants to generate. Default: 8",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible output. Default: 42",
    )
    parser.add_argument(
        "--image-format",
        choices=["png", "jpg"],
        default="png",
        help="Output image format. Default: png",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=180,
        help="DPI to use when rasterizing PDFs. Default: 180",
    )
    return parser.parse_args()


def discover_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")
    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS.union(PDF_EXTENSIONS)]
    if not files:
        raise SystemExit(f"No supported PDF/image files found in: {input_dir}")
    return sorted(files)


def open_source_as_image(path: Path, dpi: int) -> Image.Image:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return Image.open(path).convert("RGB")
    if ext in PDF_EXTENSIONS:
        if not PDF_SUPPORT:
            raise RuntimeError(
                "PDF support is unavailable. Install pdf2image and ensure poppler is installed."
            )
        pages = convert_from_path(str(path), dpi=dpi, first_page=1, last_page=1)
        if not pages:
            raise RuntimeError(f"No pages rendered from PDF: {path}")
        return pages[0].convert("RGB")
    raise RuntimeError(f"Unsupported source type: {path.suffix}")


def add_jpeg_artifacts(image: Image.Image, quality: int) -> Image.Image:
    from io import BytesIO
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def apply_noise_pipeline(image: Image.Image, rng: random.Random) -> tuple[Image.Image, list[str]]:
    steps: list[str] = []

    img = image.copy()

    if rng.random() < 0.75:
        scale = rng.uniform(0.78, 1.0)
        new_size = (max(600, int(img.width * scale)), max(800, int(img.height * scale)))
        img = img.resize(new_size)
        steps.append(f"resized_{scale:.2f}")

    if rng.random() < 0.9:
        angle = rng.uniform(-3.2, 3.2)
        img = img.rotate(angle, expand=True, fillcolor="white")
        steps.append(f"rotated_{angle:.2f}")

    if rng.random() < 0.8:
        contrast_factor = rng.uniform(0.68, 0.95)
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)
        steps.append(f"contrast_{contrast_factor:.2f}")

    if rng.random() < 0.6:
        brightness_factor = rng.uniform(0.85, 1.10)
        img = ImageEnhance.Brightness(img).enhance(brightness_factor)
        steps.append(f"brightness_{brightness_factor:.2f}")

    if rng.random() < 0.7:
        radius = rng.uniform(0.4, 1.4)
        img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        steps.append(f"blur_{radius:.2f}")

    if rng.random() < 0.35:
        img = img.convert("L").convert("RGB")
        steps.append("grayscale")

    if rng.random() < 0.75:
        quality = rng.randint(28, 62)
        img = add_jpeg_artifacts(img, quality=quality)
        steps.append(f"jpeg_q{quality}")

    return img, steps


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True) if path.suffix else path.mkdir(parents=True, exist_ok=True)


def write_manifest(path: Path, rows: list[dict]) -> None:
    ensure_dirs(path)
    fieldnames = [
        "source_file",
        "generated_file",
        "category",
        "expected_outcome",
        "transform_steps",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    ensure_dirs(args.output_dir, args.manifest_path)
    source_files = discover_files(args.input_dir)

    manifest_rows: list[dict] = []

    for idx in range(1, args.count + 1):
        source = rng.choice(source_files)
        base_image = open_source_as_image(source, dpi=args.dpi)
        noisy, steps = apply_noise_pipeline(base_image, rng)

        suffix = ".jpg" if args.image_format == "jpg" else ".png"
        out_name = f"INV_NOISY_{idx:03d}{suffix}"
        out_path = args.output_dir / out_name

        if args.image_format == "jpg":
            noisy.save(out_path, format="JPEG", quality=82, optimize=True)
        else:
            noisy.save(out_path, format="PNG")

        manifest_rows.append(
            {
                "source_file": source.name,
                "generated_file": out_name,
                "category": "noisy",
                "expected_outcome": "Needs review",
                "transform_steps": ";".join(steps),
                "notes": "Noisy image variant generated for extraction robustness testing.",
            }
        )

    write_manifest(args.manifest_path, manifest_rows)

    print(f"Generated {args.count} noisy variants in: {args.output_dir}")
    print(f"Manifest written to: {args.manifest_path}")
    if not PDF_SUPPORT:
        print("Warning: pdf2image was not available when this script ran. PDF input may fail until dependencies are installed.")


if __name__ == "__main__":
    main()
