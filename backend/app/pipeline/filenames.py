"""What a file's name says: which branch, and which week (D-015).

Files arrive named ``<branch>-<YYYY-MM-DD>[-anything].<ext>``, where the date
is the first day of the week the file covers. The name is a *claim*, used as
evidence for one thing only: which reading of an ambiguous date falls inside
the week. A name that does not follow the pattern is not an error — the file
is read without that evidence, and its ambiguous dates are held rather than
inferred.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

from app.domain.dates import Period

WEEK_DAYS = 7
_NAME = re.compile(r"^(?P<branch>[a-z]+)-(?P<date>\d{4}-\d{2}-\d{2})(?:-[^.]*)?\.[A-Za-z0-9]+$")


@dataclass(frozen=True)
class FileName:
    branch: str
    week_start: dt.date

    @property
    def period(self) -> Period:
        return self.week_start, self.week_start + dt.timedelta(days=WEEK_DAYS - 1)


def parse_file_name(name: str) -> FileName | None:
    m = _NAME.match(name)
    if m is None:
        return None
    try:
        start = dt.date.fromisoformat(m["date"])
    except ValueError:
        return None
    return FileName(m["branch"], start)
