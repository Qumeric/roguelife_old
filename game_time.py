from datetime import datetime, timedelta

from blinker import Signal

from events import TickEvent

_ticks = 0
tick_signal = Signal("tick")


def tick():
    global _ticks
    _ticks += 1
    tick_signal.send(None, event=TickEvent(current_datetime()))


def current_datetime() -> datetime:
    print(_ticks)
    return datetime(1, 1, 1) + timedelta(minutes=_ticks)
