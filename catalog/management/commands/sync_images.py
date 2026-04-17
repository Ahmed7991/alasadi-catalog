"""
Bulk-sync product images from a drop folder to Product.image fields.

Expected layout (relative to BASE_DIR):
    import_images/8051.jpg     -> matches Product.item_code="8051"
                                  (or "8051_1", "8051_2", ... as fallback)

Successfully matched files are moved to processed_images/ so re-runs
of this command skip what's already been linked.

Usage:
    python manage.py sync_images
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Product


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class Command(BaseCommand):
    help = "Bulk-sync product images from import_images/ -> Product.image."

    def handle(self, *args, **options):
        src_dir = Path(settings.BASE_DIR) / "import_images"
        dst_dir = Path(settings.BASE_DIR) / "processed_images"

        if not src_dir.exists():
            self.stderr.write(
                self.style.ERROR(f"Source folder not found: {src_dir}")
            )
            self.stderr.write(
                self.style.WARNING(f"Create it with: mkdir {src_dir}")
            )
            return

        dst_dir.mkdir(exist_ok=True)

        files = sorted(
            p for p in src_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS
        )

        if not files:
            self.stdout.write(
                self.style.WARNING(f"No image files found in {src_dir}")
            )
            return

        self.stdout.write(f"Processing {len(files)} image(s) from {src_dir}\n")

        linked = 0
        not_found = 0
        errors = 0

        for path in files:
            potential_item_code = path.stem.strip()

            # Exact match first.
            products = list(
                Product.objects.filter(item_code=potential_item_code)
            )
            match_note = ""

            # Fallback: pick up suffixed duplicates e.g. "8051_1", "8051_2".
            if not products:
                products = list(
                    Product.objects.filter(
                        item_code__startswith=f"{potential_item_code}_"
                    )
                )
                if products:
                    match_note = (
                        f" (linked to {len(products)} suffixed rows: "
                        f"{', '.join(p.item_code for p in products)})"
                    )

            if not products:
                self.stdout.write(
                    self.style.ERROR(
                        f"[Error] Code {potential_item_code} not found"
                    )
                )
                not_found += 1
                continue

            try:
                # Re-open per product so each .save() call gets a fresh read
                # handle — the storage backend consumes the stream.
                for product in products:
                    with path.open("rb") as fh:
                        product.image.save(path.name, File(fh), save=True)
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f"[Error] {path.name}: {exc}")
                )
                errors += 1
                continue

            dest = _unique_path(dst_dir, path.name)
            shutil.move(str(path), str(dest))

            self.stdout.write(
                self.style.SUCCESS(
                    f"[Success] Linked {potential_item_code}{match_note}"
                )
            )
            linked += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Linked: {linked} | Not found: {not_found} | Errors: {errors}"
            )
        )


def _unique_path(directory: Path, filename: str) -> Path:
    """Return a path inside `directory` that doesn't clash with existing files."""
    dest = directory / filename
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while (directory / f"{stem}__{counter}{suffix}").exists():
        counter += 1
    return directory / f"{stem}__{counter}{suffix}"
