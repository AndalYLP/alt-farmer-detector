import datetime as dt
import math
import re
from enum import Enum
from functools import total_ordering


def intcomma(value: "float | str", nDigits: int | None = None) -> str:
    thousands_sep, decimal_sep = ",", "."
    try:
        value = (
            float(value.replace(thousands_sep, "").replace(decimal_sep, "."))
            if isinstance(value, str)
            else float(value)
        )
        if not math.isfinite(value):
            return "NaN" if math.isnan(value) else "-Inf" if value < 0 else "+Inf"
    except (ValueError, TypeError):
        return str(value)

    orig = f"{value:.{nDigits}f}" if nDigits is not None else str(value)
    orig = orig.replace(".", decimal_sep)
    while True:
        new = re.sub(r"^(-?\d+)(\d{3})", rf"\g<1>{thousands_sep}\g<2>", orig)
        if orig == new:
            return new
        orig = new


@total_ordering
class Unit(Enum):
    SECONDS, MINUTES, HOURS, DAYS, MONTHS, YEARS = range(6)

    def __lt__(self, other):
        return self.value < other.value if isinstance(other, Unit) else NotImplemented


def _convert_aware_datetime(value):
    return (
        dt.datetime.fromtimestamp(value.timestamp())
        if isinstance(value, dt.datetime) and value.tzinfo
        else value
    )


def _abs_timedelta(delta):
    return delta if delta.days >= 0 else dt.datetime.now() - (dt.datetime.now() + delta)


def _date_and_delta(value, now=None):
    now = now or dt.datetime.now()
    if isinstance(value, dt.datetime):
        return value, _abs_timedelta(now - value)
    if isinstance(value, dt.timedelta):
        return now - value, value
    try:
        return now - dt.timedelta(seconds=int(value)), dt.timedelta(seconds=int(value))
    except (ValueError, TypeError):
        return None, value


def natural_delta(
    value: dt.timedelta | float, months: bool = True, minimum_unit: str = "seconds"
):
    min_unit = Unit[minimum_unit.upper()]
    if min_unit not in (Unit.SECONDS,):
        raise ValueError(f"Minimum unit '{minimum_unit}' not supported")
    delta = abs(
        value if isinstance(value, dt.timedelta) else dt.timedelta(seconds=float(value))
    )
    years, days = divmod(delta.days, 365)
    num_months = int(days // 30.5)
    if not years and days < 1:
        if delta.seconds < 60:
            return f"{delta.seconds} second" + ("s" if delta.seconds != 1 else "")
        if delta.seconds < 3600:
            return f"{delta.seconds // 60} minute" + (
                "s" if delta.seconds // 60 != 1 else ""
            )
        return f"{delta.seconds // 3600} hour" + (
            "s" if delta.seconds // 3600 != 1 else ""
        )
    if years == 0:
        return (
            f"{num_months if months else days} "
            + ("month" if months else "day")
            + ("s" if (num_months if months else days) != 1 else "")
        )
    return f"{years} year" + ("s" if years != 1 else "")


def natural_time(
    value: dt.datetime | dt.timedelta | float,
    future: bool = False,
    months: bool = True,
    minimum_unit: str = "seconds",
    when: dt.datetime | None = None,
):
    value, when = _convert_aware_datetime(value), _convert_aware_datetime(when)
    date, delta = _date_and_delta(value, now=when or dt.datetime.now())
    if date is None:
        return str(value)
    future = (
        date > (when or dt.datetime.now())
        if isinstance(value, (dt.datetime, dt.timedelta))
        else future
    )
    delta_str = natural_delta(delta, months, minimum_unit)
    return (
        "now"
        if delta_str == "0 seconds"
        else f"{delta_str} {'from now' if future else 'ago'}"
    )
