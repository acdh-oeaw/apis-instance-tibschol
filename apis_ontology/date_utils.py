from enum import Enum
from typing import Tuple
from datetime import datetime
from django_interval.utils import DateTuple
import re
import calendar


def last_day_of_month(year, month):
    """Return the last day of the month for the given year and month."""
    _, last_day = calendar.monthrange(year, month)
    return last_day


def incomplete_date_to_interval(
    date_string: str,
) -> Tuple[datetime, datetime, datetime]:
    dates = DateTuple()

    date_parts = date_string.split("-")
    year = int(date_parts[0])
    month, day = None, None
    from_date, to_date = None, None
    if len(date_parts) > 1:
        month = int(date_parts[1])
    if len(date_parts) > 2:
        # complete date
        day = int(date_parts[2])

    if not month:
        from_date = datetime(year, 1, 1)
        to_date = datetime(year, 12, 31)
    elif not day:
        from_date = datetime(year, month, 1)
        to_date = datetime(year, month, last_day_of_month(year, month))
    else:
        from_date = datetime(year, month, day)
        to_date = from_date

    dates.set_range(from_date, to_date)
    return dates.tuple()


def tibschol_dateparser(
    date_string: str,
) -> Tuple[datetime, datetime, datetime]:
    date_string = date_string.lower().strip()
    dates = DateTuple()
    try:
        if "before" in date_string or "after" in date_string:
            # a closed or an open date range
            pattern_desc_range = (
                r"\b(after|before)\s+(\S+)(?:\s+(before|after)\s+(\S+))?"
            )
            matches_desc_range = re.finditer(pattern_desc_range, date_string)

            groups_desc_range = {}
            for match in matches_desc_range:
                groups_desc_range[match.group(1)] = match.group(2)
                if match.group(3):
                    groups_desc_range[match.group(3)] = match.group(4)

            if groups_desc_range:
                for desc, date in groups_desc_range.items():
                    _, interval_start, interval_end = incomplete_date_to_interval(date)
                    if desc == "after":
                        dates.from_date = interval_start
                    elif desc == "before":
                        dates.to_date = interval_end

            if dates.from_date and dates.to_date:
                dates.set_range(dates.from_date, dates.to_date)
            else:
                dates.sort_date = dates.from_date or dates.to_date
        else:
            # single date or a single incomplete date
            dates.sort_date, dates.from_date, dates.to_date = (
                incomplete_date_to_interval(date_string)
            )
    except Exception as e:
        if date_string.strip() != "" and len(date_string) > 3:
            raise ValueError(f"Could not parse date: {date_string}")

    return dates.tuple()
