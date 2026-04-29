import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from converter.models import CellTower


class Command(BaseCommand):
    help = "Load cell towers from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to CSV with cell coordinates")
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete existing cell towers before import",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        if options["truncate"]:
            CellTower.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing cell_towers records removed."))

        created = 0
        updated = 0

        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required = {"cell_id", "latitude", "longitude"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise CommandError(
                    "CSV must include columns: cell_id, latitude, longitude "
                    "(optional: cell_name, region, site_name)"
                )

            for row in reader:
                if not row.get("cell_id"):
                    continue

                defaults = {
                    "cell_name": row.get("cell_name") or None,
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                    "region": row.get("region") or None,
                    "site_name": row.get("site_name") or None,
                }

                _, was_created = CellTower.objects.update_or_create(
                    cell_id=row["cell_id"].strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cell import complete. Created: {created}, Updated: {updated}, Total: {CellTower.objects.count()}"
            )
        )
