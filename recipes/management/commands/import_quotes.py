import csv
from django.core.management.base import BaseCommand
from recipes.models import Quote


class Command(BaseCommand):
    help="Import quotes from data/raw/quotes.csv"

    def handle(self, *args, **kwargs):
        file_path="data/raw/quotes.csv"

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader=csv.DictReader(csvfile)

            for row in reader:
                quote_id=row["ID"].strip()
                quote_text=row["Quote"].strip()

                if not quote_id or not quote_text:
                    continue

                Quote.objects.update_or_create(
                    id=int(quote_id),
                    defaults={
                        "quote": quote_text,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Quotes imported successfully."))