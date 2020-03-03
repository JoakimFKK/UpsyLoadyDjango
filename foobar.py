from datetime import datetime

YEAR_CHOICES = [(year, year) for year in reversed(range(2000, datetime.now().year + 1))]
