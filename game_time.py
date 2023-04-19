from datetime import datetime, timedelta

_ticks = 0


def tick():
    global _ticks
    _ticks += 1


def current_datetime() -> datetime:
    print(_ticks)
    return datetime(1, 1, 1) + timedelta(minutes=_ticks)
