#!/usr/bin/env python3
"""Generate responsive WebP copies without modifying original assets. Requires Pillow."""
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageFile

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'assets/images'
PREVIEWS = IMAGES / 'previews'
OPTIMIZED = IMAGES / 'optimized'
ImageFile.LOAD_TRUNCATED_IMAGES = True


def web_copy(image, path, edge, quality):
    copy = image.copy()
    copy.thumbnail((edge, edge), Image.Resampling.LANCZOS)
    copy.save(path, 'WEBP', quality=quality, method=5)
    return {'url': path.relative_to(ROOT).as_posix(), 'width': copy.width,
            'height': copy.height, 'bytes': path.stat().st_size}


def main():
    PREVIEWS.mkdir(exist_ok=True)
    OPTIMIZED.mkdir(exist_ok=True)
    manifest, dimensions, stems = {}, {}, set()
    for path in sorted(IMAGES.rglob('*')):
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg') or any(
                folder in path.relative_to(IMAGES).parts for folder in ('previews', 'optimized')):
            continue
        if path.stem in stems:
            raise SystemExit(f'Duplicate image stem: {path.stem}')
        stems.add(path.stem)
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            image = image.convert('RGBA' if 'A' in image.getbands() or 'transparency' in image.info else 'RGB')
            preview = web_copy(image, PREVIEWS / (path.stem + '.webp'), 1440, 86)
            variants = []
            for width in ((128, 480, 960) if path.name == 'logo.png' else (480, 960)):
                if preview['width'] <= width:
                    continue
                small = image.copy()
                small.thumbnail((width, 1440), Image.Resampling.LANCZOS)
                variant_path = PREVIEWS / f'{path.stem}-{small.width}w.webp'
                small.save(variant_path, 'WEBP', quality=84, method=5)
                variants.append({'url': variant_path.relative_to(ROOT).as_posix(), 'width': small.width,
                                 'height': small.height, 'bytes': variant_path.stat().st_size})
            variants.append(preview)
            full = web_copy(image, OPTIMIZED / (path.stem + '.webp'), 2560, 92)
            key = path.relative_to(IMAGES).as_posix()
            manifest[key] = {'original_bytes': path.stat().st_size, 'preview': preview, 'variants': variants, 'full': full}
            dimensions[path.stem] = [preview['width'], preview['height']]
            if path.name == 'foto_RinaldiMichele_1.png':
                # Keep the original transparent PNG as explicitly requested.
                obsolete = OPTIMIZED / path.name
                if obsolete.exists():
                    obsolete.unlink()
                manifest[key]['png'] = {'url': path.relative_to(ROOT).as_posix(), 'width': source.width,
                                       'height': source.height, 'bytes': path.stat().st_size}
    (ROOT / 'data/images.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'data/image-sizes.json').write_text(json.dumps(dimensions, indent=2) + '\n')
    original = sum(item['original_bytes'] for item in manifest.values())
    full = sum(item['full']['bytes'] for item in manifest.values())
    preview = sum(item['preview']['bytes'] for item in manifest.values())
    report = {'images': len(manifest), 'original_bytes': original, 'full_webp_bytes': full,
              'preview_bytes': preview, 'full_saving_percent': round((1 - full / original) * 100, 1)}
    (ROOT / 'data/image-optimization.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
